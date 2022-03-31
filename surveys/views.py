from datetime import datetime
from django.db.models import Max
from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from surveys.models import Survey
from surveys.serializes import SurveySerializer, QuestionSerializer, AnswerSerializer
from users.models import UserAnswer


def question(request, survey_id, question_pos_in_survey):
    if request.method == 'POST':
        survey = Survey.objects.get(id=survey_id)
        user = request.user
        question = survey.questions.all()[question_pos_in_survey - 1]
        answer = request.POST['answer']
        if str(question.type) == 'Text':
            instance = UserAnswer.objects.create(
                user=user,
                user_anonymous=0,
                answer_text=answer
            )
        else:
            instance = UserAnswer.objects.create(
                user=user,
                user_anonymous=False
            )
            for ans in answer:
                instance.answer_choose.set(question.answers.filter(id=ans))
        instance.survey.set((survey,))
        instance.question.set((question,))
        if question_pos_in_survey == len(survey.questions.all()):
            return HttpResponseRedirect(reverse('survey:complete'))
        else:
            return HttpResponseRedirect(reverse('survey:question',
                                                kwargs={'survey_id': survey_id,
                                                        'question_pos_in_survey': question_pos_in_survey + 1}))
    else:
        survey = Survey.objects.get(id=survey_id)
        question = survey.questions.all()[question_pos_in_survey - 1]
        context = {'survey': survey, 'question': question,
                   'question_pos_in_survey': question_pos_in_survey}
        return render(request, 'surveys/question.html', context)


@api_view(['GET'])
def api_surveys_list(request):
    if request.method == 'GET':
        surveys = Survey.objects.filter(date_end__gt=datetime.now())
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def api_survey(request, pk):
    if request.method == 'GET':
        survey = get_object_or_404(Survey, pk=pk)
        if survey:
            survey_outdated = survey.date_end.timestamp() < datetime.now().timestamp()
        else:
            survey_outdated = False
        serializer = SurveySerializer(survey)
        print(type(survey))
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def api_question(request, pk_survey, pk_question):
    if request.method == 'GET':
        survey = get_object_or_404(Survey, pk=pk_survey)
        if survey:
            question_ = survey.questions.all()[pk_question - 1]
        else:
            question_ = []
        serializer = QuestionSerializer(question_)
        return Response(serializer.data)
    elif request.method == 'POST':
        survey = Survey.objects.get(id=pk_survey)
        question_ = survey.questions.all()[pk_question - 1]
        data = {'survey': survey, 'question': question_}
        user = request.user
        if user and user.is_active:
            data['user'] = user
        else:
            data['user_anonymous_id'] = request.data['user_anonymous_id']
        if question_.type.id == 1:
            data['answer_text'] = request.data['answer']
        else:
            data['answer_choose'] = request.data['answers_array']
        serializer = AnswerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
