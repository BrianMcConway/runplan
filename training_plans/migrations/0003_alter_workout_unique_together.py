# Generated by Django 4.2.15 on 2024-08-31 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training_plans', '0002_alter_workout_options_alter_workout_description'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='workout',
            unique_together={('training_plan', 'week_number', 'day_of_week')},
        ),
    ]
