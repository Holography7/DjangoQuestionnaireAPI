from django.db import models


class QuestionType(models.Model):
    type = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.type


class AnswersVariants(models.Model):
    answer = models.CharField(max_length=256)

    def __str__(self):
        return self.answer


class Question(models.Model):
    question = models.TextField()
    type = models.ForeignKey(QuestionType, on_delete=models.PROTECT)
    answers = models.ManyToManyField(AnswersVariants, blank=True)

    def __str__(self):
        return self.question


class Survey(models.Model):
    name = models.CharField(max_length=64, unique=True)
    date_start = models.DateTimeField(auto_now_add=True, editable=False)
    date_end = models.DateTimeField()
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.name
