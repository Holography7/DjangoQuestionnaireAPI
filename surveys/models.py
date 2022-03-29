from django.db import models


class QuestionType(models.Model):
    def __str__(self):
        return self.type
    type = models.CharField(max_length=32, unique=True)


class AnswersVariants(models.Model):
    def __str__(self):
        return self.answer
    answer = models.CharField(max_length=256)


class Question(models.Model):
    def __str__(self):
        return self.question
    question = models.TextField()
    type = models.ForeignKey(QuestionType, on_delete=models.PROTECT)
    answers = models.ManyToManyField(AnswersVariants, blank=True)


class Survey(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=64, unique=True)
    date_start = models.DateTimeField(auto_now_add=True, editable=False)
    date_end = models.DateTimeField()
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question)
