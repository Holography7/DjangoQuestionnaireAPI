from rest_framework import serializers
from surveys.models import Survey, Question, AnswersVariants


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswersVariants
        fields = ('id', 'answer')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, allow_null=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'type', 'answers')


class SurveySerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = ('name', 'date_end', 'description')


class SurveyActiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = ('name', 'date_end', 'description')


class SurveyCompletedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = ('name', 'description')
