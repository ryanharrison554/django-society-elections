# Generated by Django 3.2.7 on 2021-10-18 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('society_elections', '0003_candidate_manifesto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voter',
            name='email_salt',
        ),
    ]
