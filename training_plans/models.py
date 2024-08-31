from django.db import models
from django.contrib.auth.models import User

class TrainingPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration_weeks = models.PositiveIntegerField()
    skill_level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    distance_km = models.FloatField()  # Distance of the event in km
    elevation_gain_m = models.PositiveIntegerField()  # Total elevation gain in meters

    def __str__(self):
        return self.name


class Workout(models.Model):
    training_plan = models.ForeignKey(
        TrainingPlan, 
        on_delete=models.CASCADE, 
        related_name='workouts'
    )
    week_number = models.PositiveIntegerField()
    day_of_week = models.CharField(max_length=20, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    workout_type = models.CharField(max_length=50, choices=[
        ('easy_run', 'Easy Run'),
        ('long_run', 'Long Run'),
        ('tempo_run', 'Tempo Run'),
        ('intervals', 'Intervals'),
        ('hill_repeats', 'Hill Repeats'),
        ('rest', 'Rest'),
        ('cross_training', 'Cross Training'),
    ])
    description = models.TextField(blank=True)  # Allow description to be optional
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    elevation_gain_m = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['week_number', 'day_of_week']  # Ensure workouts are ordered by week and day
        unique_together = ('training_plan', 'week_number', 'day_of_week')  # Prevent duplicate workouts on the same day

    def __str__(self):
        return f"Week {self.week_number} - {self.day_of_week}: {self.workout_type}"


class UserTrainingPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.training_plan.name}"
