from django.db import models
from django.contrib.auth.models import AbstractUser

from surveys.models import Survey, Question, AnswersVariants


class User(AbstractUser):
    age = models.PositiveSmallIntegerField(default=18)


class UserStatusInSurveys(models.Model):
    user = models.ManyToManyField(User)
    survey = models.ManyToManyField(Survey)
    completed = models.BooleanField(default=False)


class AnonymousUserStatusInSurveys(models.Model):
    survey = models.ManyToManyField(Survey)
    completed = models.BooleanField(default=False)


class UserAnswer(models.Model):
    survey = models.ManyToManyField(Survey)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, default=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)
    answer_text = models.TextField(blank=True)
    answer_choose = models.ManyToManyField(AnswersVariants, blank=True)


class AnonymousUserAnswer(models.Model):
    survey = models.ManyToManyField(Survey)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, default=0)
    user_anonymous_id = models.ForeignKey(AnonymousUserStatusInSurveys, on_delete=models.PROTECT, default=0)
    answer_text = models.TextField(blank=True)
    answer_choose = models.ManyToManyField(AnswersVariants, blank=True)
