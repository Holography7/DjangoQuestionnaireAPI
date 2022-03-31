# Generated by Django 3.2.12 on 2022-03-31 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
        ('users', '0004_alter_useranswer_answer_choose'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useranswer',
            name='question',
        ),
        migrations.AddField(
            model_name='useranswer',
            name='question',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='surveys.question'),
        ),
    ]
