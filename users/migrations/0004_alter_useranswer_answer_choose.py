# Generated by Django 3.2.12 on 2022-03-31 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
        ('users', '0003_auto_20220331_0738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='answer_choose',
            field=models.ManyToManyField(blank=True, to='surveys.AnswersVariants'),
        ),
    ]
