# Generated by Django 5.0 on 2024-01-04 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Wildfires',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('brightness', models.FloatField()),
                ('scan', models.FloatField()),
                ('track', models.FloatField()),
                ('acq_date', models.DateTimeField()),
                ('acq_time', models.IntegerField()),
                ('satellite', models.CharField(max_length=255)),
                ('instrument', models.CharField(max_length=255)),
                ('confidence', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('bright_t31', models.FloatField()),
                ('frp', models.FloatField()),
                ('daynight', models.CharField(max_length=255)),
                ('type', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
