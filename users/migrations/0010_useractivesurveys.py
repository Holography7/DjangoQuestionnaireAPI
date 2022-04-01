# Generated by Django 3.2.12 on 2022-04-01 09:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_rename_answer_1_answersvariants_answer'),
        ('users', '0009_auto_20220401_0659'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActiveSurveys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_surveys', models.ManyToManyField(to='surveys.Survey')),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
