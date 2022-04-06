from django.db import models
from django.contrib.auth.models import AbstractUser

from surveys.models import Survey, Question, AnswersVariants


class User(AbstractUser):
    age = models.PositiveSmallIntegerField(default=18)


class UserStatusInSurveys(models.Model):
    def __str__(self):
        return self.user.all()[0].username
    user = models.ManyToManyField(User)
    survey = models.ManyToManyField(Survey)
    completed = models.BooleanField(default=False)


class AnonymousUserStatusInSurveys(models.Model):
    def __str__(self):
        return str(self.user_anonymous_id)
    user_anonymous_id = models.PositiveIntegerField(default=0)
    survey = models.ManyToManyField(Survey)
    completed = models.BooleanField(default=False)


class UserAnswer(models.Model):
    def __str__(self):
        return self.user
    survey = models.ManyToManyField(Survey)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, default=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)
    answer_text = models.TextField(blank=True)
    answer_choose = models.ManyToManyField(AnswersVariants, blank=True)


class AnonymousUserAnswer(models.Model):
    def __str__(self):
        return str(self.user_anonymous_id)
    survey = models.ManyToManyField(Survey)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, default=0)
    user_anonymous_id = models.PositiveIntegerField(default=0)
    answer_text = models.TextField(blank=True)
    answer_choose = models.ManyToManyField(AnswersVariants, blank=True)
