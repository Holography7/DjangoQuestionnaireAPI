from django.db import models
from django.contrib.auth.models import AbstractUser

from surveys.models import Survey, Question, AnswersVariants


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True)


class UserAnswer(models.Model):
    survey = models.ManyToManyField(Survey, blank=True)
    question = models.ManyToManyField(Question)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    user_anonymous = models.BooleanField(default=False)
    answer_text = models.TextField(blank=True)
    answer_choose = models.ManyToManyField(AnswersVariants)
