from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TrainingPlanForm
from .models import TrainingPlan, Workout, UserTrainingPlan
from datetime import datetime, timedelta

def home(request):
    return render(request, 'index.html')

@login_required
def generate_training_plan(request):
    if request.method == 'POST':
        form = TrainingPlanForm(request.POST)
        if form.is_valid():
            event_date = form.cleaned_data['event_date']
            distance_km = form.cleaned_data['distance_km']
            elevation_gain_m = form.cleaned_data['elevation_gain_m']
            skill_level = form.cleaned_data['skill_level']
            training_days_per_week = int(form.cleaned_data['training_days_per_week'])

            # Calculate the number of weeks until the event
            today = datetime.now().date()
            start_date = today + timedelta(days=(7 - today.weekday())) if today.weekday() != 0 else today
            days_until_event = (event_date - start_date).days
            weeks_until_event = days_until_event // 7

            # Validate that the event date is in the future
            if days_until_event <= 0:
                messages.error(request, "The event date must be in the future.")
                return render(request, 'training_plans/generate_training_plan.html', {'form': form})

            # Select or create a training plan based on user input
            training_plan, created = TrainingPlan.objects.get_or_create(
                name=f"Custom Plan for {distance_km}km",
                defaults={
                    'description': f"A training plan generated for a {skill_level} runner preparing for a {distance_km}km event.",
                    'duration_weeks': weeks_until_event,
                    'skill_level': skill_level,
                    'distance_km': distance_km,
                    'elevation_gain_m': elevation_gain_m
                }
            )

            # Generate workouts for the training plan
            try:
                generate_workouts(training_plan, weeks_until_event, skill_level, distance_km, elevation_gain_m, training_days_per_week, start_date)
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'training_plans/generate_training_plan.html', {'form': form})

            # Associate the training plan with the user
            user_plan = UserTrainingPlan.objects.create(
                user=request.user,
                training_plan=training_plan,
                start_date=start_date,
                end_date=event_date,
            )

            return redirect('training_plans:view_training_plan', pk=user_plan.pk)
    else:
        form = TrainingPlanForm(initial={'event_date': datetime.now().date()})

    return render(request, 'training_plans/generate_training_plan.html', {'form': form})

@login_required
def view_training_plan(request, pk):
    user_training_plan = get_object_or_404(UserTrainingPlan, pk=pk, user=request.user)
    workouts = user_training_plan.training_plan.workouts.order_by('week_number', 'day_of_week')

    # Prepare the days of the week for the template
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    grouped_workouts_with_dates = []
    for week_number in range(1, user_training_plan.training_plan.duration_weeks + 1):
        week_start_date = (user_training_plan.start_date + timedelta(weeks=week_number - 1)).strftime("%B %d, %Y")
        weekly_workouts = workouts.filter(week_number=week_number).order_by('day_of_week')
        grouped_workouts_with_dates.append({
            'week_number': week_number,
            'start_date': week_start_date,
            'workouts': weekly_workouts
        })

    return render(request, 'training_plans/view_training_plan.html', {
        'user_training_plan': user_training_plan,
        'grouped_workouts_with_dates': grouped_workouts_with_dates,
        'days_of_week': days_of_week,  # Pass the days of the week to the template
    })

def generate_workouts(training_plan, weeks_until_event, skill_level, distance_km, elevation_gain_m, training_days_per_week, start_date):
    # Clear existing workouts for this training plan
    training_plan.workouts.all().delete()
    
    # Base distances for different skill levels
    distances = {'beginner': 5, 'intermediate': 8, 'advanced': 10}
    weekly_increase = {'beginner': 1.1, 'intermediate': 1.15, 'advanced': 1.2}
    current_distance = distances[skill_level]

    # Define the fixed weekly plan
    fixed_workout_days = {
        'Monday': 'easy_run',
        'Tuesday': 'intervals',
        'Wednesday': 'rest',  # Fixed Rest day
        'Thursday': 'hill_repeats',
        'Friday': 'tempo_run',
        'Saturday': 'long_run',  # Long run
        'Sunday': 'cross_training'  # Cross training
    }

    # Define the number of rest days based on training days per week
    rest_days_needed = 7 - training_days_per_week

    # Ensure Wednesday is always a rest day
    rest_days = ['Wednesday']

    # Distribute remaining rest days dynamically
    possible_rest_days = ['Monday', 'Tuesday', 'Thursday', 'Friday', 'Sunday']

    for day in possible_rest_days:
        if len(rest_days) < rest_days_needed:
            rest_days.append(day)

    # Create a dynamic weekly plan based on the rest days
    dynamic_weekly_plan = fixed_workout_days.copy()
    for day in rest_days:
        dynamic_weekly_plan[day] = 'rest'

    # Ensure no consecutive rest days
    for i in range(len(possible_rest_days) - 1):
        if dynamic_weekly_plan[possible_rest_days[i]] == 'rest' and dynamic_weekly_plan[possible_rest_days[i + 1]] == 'rest':
            # Swap the next rest day to avoid consecutive rest days
            next_non_rest_day = next(day for day in possible_rest_days[i + 2:] if dynamic_weekly_plan[day] != 'rest')
            dynamic_weekly_plan[possible_rest_days[i + 1]], dynamic_weekly_plan[next_non_rest_day] = (
                dynamic_weekly_plan[next_non_rest_day],
                dynamic_weekly_plan[possible_rest_days[i + 1]],
            )

    # Create workouts based on the dynamic weekly plan
    for week in range(1, weeks_until_event + 1):
        current_monday = start_date + timedelta(weeks=week - 1)

        for day_name, workout_type in dynamic_weekly_plan.items():
            day_index = list(fixed_workout_days.keys()).index(day_name)
            workout_date = current_monday + timedelta(days=day_index)

            # Calculate distance and elevation based on workout type
            if workout_type == 'rest':
                distance = 0
                elevation = 0
            elif workout_type == 'easy_run':
                distance = round(min(current_distance * 0.5, distance_km * 0.5))
                elevation = 0
            elif workout_type == 'tempo_run':
                distance = round(min(current_distance * 0.7, distance_km * 0.7))
                elevation = 0
            elif workout_type == 'intervals':
                distance = round(min(current_distance * 0.3, distance_km * 0.3))
                elevation = 0
            elif workout_type == 'long_run':
                distance = round(min(current_distance * 1.5, distance_km))
                elevation = 0
            elif workout_type == 'hill_repeats':
                distance = round(min(current_distance * 0.4, distance_km * 0.4))
                elevation = round(elevation_gain_m * 0.1)
            elif workout_type == 'cross_training':
                distance = 0
                elevation = 0

            # Create workout entry
            Workout.objects.create(
                training_plan=training_plan,
                week_number=week,
                day_of_week=day_name,
                workout_type=workout_type,
                description=f'{workout_type.replace("_", " ").capitalize()} on {workout_date.strftime("%A, %B %d")}',
                distance_km=distance,
                elevation_gain_m=elevation,
                duration_minutes=None  # Add duration calculation if needed
            )

        # Increase the base distance for the next week but ensure it does not exceed the event distance
        current_distance = min(current_distance * weekly_increase[skill_level], distance_km)
