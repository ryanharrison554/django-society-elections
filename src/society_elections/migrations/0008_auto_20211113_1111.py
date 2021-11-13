# Generated by Django 3.2.7 on 2021-11-13 11:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('society_elections', '0007_auto_20211101_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='election',
            name='results_submitted',
        ),
        migrations.RemoveField(
            model_name='election',
            name='results_submitted_at',
        ),
        migrations.RemoveField(
            model_name='election',
            name='results_submitted_by',
        ),
        migrations.AddField(
            model_name='election',
            name='ended_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='election',
            name='ended_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='elections_ended', related_query_name='election_ended', to=settings.AUTH_USER_MODEL),
        ),
    ]