from datetime import datetime
from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from surveys.models import Survey
from surveys.serializes import SurveySerializer, QuestionSerializer
from users.models import UserAnswer, AnonymousUserAnswer, UserStatusInSurveys
from users.serializes import UserAnswerSerializer, AnonymousUserAnswerSerializer, UserStatusInSurveysSerializer


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
        if survey.date_end.timestamp() > datetime.now().timestamp():
            serializer = SurveySerializer(survey)
            data = serializer.data
            data.update({"questions_count": survey.questions.all().count()})
            return Response(data)
        else:
            return Response({"survey": "outdated"},
                            status=status.HTTP_423_LOCKED)
    elif request.method == 'POST':
        user = request.user
        survey = get_object_or_404(Survey, pk=pk)
        if not user or not user.is_active:
            if AnonymousUserAnswer.objects.all():
                user_anonymous_id = AnonymousUserAnswer.objects.aggregate(Max('user_anonymous_id'))
                user_anonymous_id['user_anonymous_id'] += 1
            else:
                user_anonymous_id = {'user_anonymous_id': 1}
            return Response(user_anonymous_id, status=status.HTTP_202_ACCEPTED)
        serializer = UserStatusInSurveysSerializer(data={'user': (user.id,), 'survey': (survey.id,),
                                                         'completed': False})
        if serializer.is_valid():
            serializer.save()
            return Response({'survey': 'started'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_complete_survey(request, pk):
    if request.method == 'GET':
        user = request.user
        if user and user.is_active:
            user_status_in_survey = UserStatusInSurveys.objects.filter(user=user.id, survey=pk)
            if user_status_in_survey[0].completed:
                return Response({'user': 'already completed this survey'}, status=status.HTTP_400_BAD_REQUEST)
            answered_questions = UserAnswer.objects.filter(user=user.id).count()
            survey = get_object_or_404(Survey, pk=pk)
            questions = survey.questions.all().count()
            if answered_questions == questions:
                user_status = UserStatusInSurveys.objects.get(user=user.id)
                serializer = UserStatusInSurveysSerializer(user_status, data={'completed': True}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'user': 'not all questions answered'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'user': 'this function not allowed for anonymous user'},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PATCH'])
def api_question(request, pk_survey, pk_question):
    if request.method == 'GET':
        survey = get_object_or_404(Survey, pk=pk_survey)
        question = survey.questions.all()[pk_question - 1]
        serializer = QuestionSerializer(question)
        return Response(serializer.data)
    elif request.method == 'POST':
        user = request.user
        survey = Survey.objects.get(id=pk_survey)
        question = survey.questions.all()[pk_question - 1]
        if user and user.is_active:
            user_active_survey = UserStatusInSurveys.objects.filter(user=user.id, survey=survey.id)
            if not user_active_survey:
                return Response({"user": "active survey before send answer"}, status=status.HTTP_400_BAD_REQUEST)
            user_answer = UserAnswer.objects.filter(user=user.id, survey=survey.id, question=question.id)
            if user_answer:
                return Response({"user": "This user already answered. Use PATCH request instead of POST for changing"},
                                status=status.HTTP_400_BAD_REQUEST)
        data = {'survey': (survey.id,), 'question': question.id}
        if question.type.id == 1:
            data['answer_text'] = request.data.get('answer')
        else:
            data['answer_choose'] = request.data.get('answer')
        if user and user.is_active:
            data['user'] = user.id
            serializer = UserAnswerSerializer(data=data)
        else:
            data['user_anonymous_id'] = request.data.get('user_anonymous_id')
            serializer = AnonymousUserAnswerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        user = request.user
        survey = Survey.objects.get(id=pk_survey)
        question = survey.questions.all()[pk_question - 1]
        if question.type.id == 1:
            data = {'answer_text': request.data.get('answer')}
        else:
            data = {'answer_choose': request.data.get('answer')}
        if user and user.is_active:
            user_answer = UserAnswer.objects.get(user=user.id, survey=survey.id, question=question.id)
            serializer = UserAnswerSerializer(user_answer, data=data, partial=True)
        else:
            user_answer = AnonymousUserAnswer.objects.get(user_anonymous_id=request.data.get('user_anonymous_id'),
                                                          survey=survey.id, question=question.id)
            data.update({'user_anonymous_id': request.data.get('user_anonymous_id')})
            serializer = AnonymousUserAnswerSerializer(user_answer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
