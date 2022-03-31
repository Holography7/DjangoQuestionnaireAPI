from django.db import models
from django.contrib.auth.models import AbstractUser

from surveys.models import Survey, Question, AnswersVariants


class User(AbstractUser):
    completed_surveys = models.ManyToManyField(Survey, blank=True)


class UserAnswer(models.Model):
    survey = models.ManyToManyField(Survey, blank=True)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, default=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)
    user_anonymous_id = models.PositiveIntegerField(default=0)
    answer_text = models.TextField(blank=True)
    answer_choose = models.ManyToManyField(AnswersVariants, blank=True)
