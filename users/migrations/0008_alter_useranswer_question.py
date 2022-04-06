# Generated by Django 3.2.12 on 2022-04-01 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_rename_answer_1_answersvariants_answer'),
        ('users', '0007_alter_useranswer_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='question',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='surveys.question'),
        ),
    ]