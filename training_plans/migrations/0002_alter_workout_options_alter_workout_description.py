# Generated by Django 4.2.15 on 2024-08-31 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training_plans', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workout',
            options={'ordering': ['week_number', 'day_of_week']},
        ),
        migrations.AlterField(
            model_name='workout',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
