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
    """Returns list with surveys that currently is available (not outdated)."""
    if request.method == 'GET':
        surveys = Survey.objects.filter(date_end__gt=datetime.now())
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def api_survey(request, pk):
    """GET request returns information about survey. You can get survey id from /survey/api/surveys.

    POST request using to begin survey so no parameters need to send (but user information still required).
    If user is anonymous, don't forget to get from server answer field user_anonymous_id and save it for user somewhere:
    this id is required to send answers for this anonymous user."""
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
        if UserStatusInSurveys.objects.filter(user=user.id, survey=survey.id):
            return Response({'user': 'this user already begin or complete this survey'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserStatusInSurveysSerializer(data={'user': (user.id,), 'survey': (survey.id,),
                                                         'completed': False})
        if serializer.is_valid():
            serializer.save()
            return Response({'survey': 'started'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def api_complete_survey(request, pk):
    """This request same as for beginning survey, just send empty POST. For anonymous user this request don't need
    because server not saving status in survey for anonymous users."""
    if request.method == 'POST':
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
    """GET request returns information about question.

    pk_survey - actually it's id survey, that you can know from survey information
    (GET /survey/api/surveys/<int:survey_id>), pk_question - it's a number of order question in survey, so it's just a
    value from 1 to questions_count that you can get from survey information (GET /survey/api/surveys/<int:survey_id>).
    Don't forget that you cannot get access to question before you don't begin survey
    (POST /survey/api/surveys/<int:survey_id>).

    POST request is sending answer to question. There are 3 options in relation to question type:
    1. Text: {"answer": "text"}
    2. Radio: {"answer": [1]}
    3. Checkbox: {"answer": [1, 2, 3]}.

    Question type you can get from GET request of this URL.
    Don't forget to add field "user_anonymous_id" into POST request for anonymous user.
    Remember that you cannot edit answer using POST request, use PATCH instead in this URL."""
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
