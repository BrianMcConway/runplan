from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class TrainingPlanForm(forms.Form):
    event_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'  # Optional: add a Bootstrap class for styling
            }
        ),
        label='Event Date'
    )
    distance_km = forms.FloatField(
        label='Event Distance (km)',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'  # Optional: add a Bootstrap class for styling
            }
        )
    )
    elevation_gain_m = forms.IntegerField(
        label='Total Elevation Gain (m)',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'  # Optional: add a Bootstrap class for styling
            }
        )
    )
    skill_level = forms.ChoiceField(
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control'  # Optional: add a Bootstrap class for styling
            }
        )
    )
    training_days_per_week = forms.ChoiceField(
        choices=[(i, f'{i} days per week') for i in range(3, 7)],
        label='Training Days Per Week',
        widget=forms.Select(
            attrs={
                'class': 'form-control'  # Optional: add a Bootstrap class for styling
            }
        )
    )

    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date < date.today():
            raise ValidationError("The event date cannot be in the past.")
        return event_date
