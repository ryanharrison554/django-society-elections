# Generated by Django 3.2.7 on 2021-11-01 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('society_elections', '0006_auto_20211101_1735'),
    ]

    operations = [
        migrations.AddField(
            model_name='electionposition',
            name='allow_abstain',
            field=models.BooleanField(default=True, help_text='Whether or not to allow voters to abstain from voting for this position'),
        ),
        migrations.AddField(
            model_name='electionposition',
            name='allow_ron',
            field=models.BooleanField(default=True, help_text='Whether or not to include "Re-open Nominations" in the list of options for voters'),
        ),
    ]
