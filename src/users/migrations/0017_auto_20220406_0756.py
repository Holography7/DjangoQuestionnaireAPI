# Generated by Django 3.2.12 on 2022-04-06 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20220405_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='anonymoususerstatusinsurveys',
            name='user_anonymous_id',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='anonymoususeranswer',
            name='user_anonymous_id',
            field=models.PositiveIntegerField(default=0),
        ),
    ]