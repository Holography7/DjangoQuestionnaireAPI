# Generated by Django 3.2.12 on 2022-04-05 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_rename_answer_1_answersvariants_answer'),
        ('users', '0013_auto_20220401_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousUserStatusInSurveys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('survey', models.ManyToManyField(to='surveys.Survey')),
            ],
        ),
    ]