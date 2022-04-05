from datetime import datetime
import pytz
from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.exceptions import PermissionDenied, ParseError, NotAuthenticated


from surveys.models import Survey, Question
from surveys.serializes import SurveySerializer, QuestionSerializer
from users.models import UserAnswer, AnonymousUserAnswer, UserStatusInSurveys, AnonymousUserStatusInSurveys
from users.serializes import UserAnswerSerializer, AnonymousUserAnswerSerializer, UserStatusInSurveysSerializer
from users.serializes import AnonymousUserStatusInSurveysSerializer, CompleteSurveySerializer


class SurveyListAPIView(ListAPIView):
    """Returns list of active (not outdated) surveys."""
    serializer_class = SurveySerializer

    def get_queryset(self):
        return Survey.objects.filter(date_end__gt=pytz.UTC.localize(datetime.now()))


class SurveyAPIView(RetrieveAPIView):
    """Returns information about survey. You can get survey id from api/survey/list/ ."""
    serializer_class = SurveySerializer

    def get_queryset(self):
        self.queryset = Survey.objects.filter(id=self.kwargs['pk'])
        if self.queryset[0].date_end > pytz.UTC.localize(datetime.now()):
            return self.queryset
        else:
            raise PermissionDenied(detail='This survey is outdated')


class QuestionsListAPIView(ListAPIView):
    """Returns list of questions from survey.

    Remember that you cannot get access there if survey outdated, user not send POST to api/survey/<int:id>/start/ to
    start survey or already complete this survey."""
    serializer_class = QuestionSerializer

    def get_queryset(self):
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        user = self.request.user
        if user and user.is_active:
            user_status = UserStatusInSurveys.objects.filter(user=user.id, survey=self.kwargs['pk'])
            if not user_status:
                raise PermissionDenied(detail="This user didn't start this survey")
            if user_status[0].completed:
                raise PermissionDenied(detail='This user already complete this survey')
            else:
                return survey.questions.all()
        return survey.questions.all()


class StartSurveyCreateAPIView(CreateAPIView):
    """Use this request to start survey as authenticated user.

    You cannot use this method as anonymous, use /api/survey/<int:pk>/start/anonymous/ instead."""
    serializer_class = UserStatusInSurveysSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if not user or not user.is_active:
            raise NotAuthenticated('This POST request method allowed only for registered users. ' +
                                   'For anonymous use api/survey/<int:pk>/start/anonymous')
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        if UserStatusInSurveys.objects.filter(user=user.id, survey=survey.id):
            raise ParseError(detail='This user already start or complete this survey.')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StartSurveyAsAnonymousCreateAPIView(CreateAPIView):
    """Use this request to start survey as anonymous user.

    You cannot use this method as authenticated user, use /api/survey/<int:pk>/start/ instead."""
    serializer_class = AnonymousUserStatusInSurveysSerializer

    def create(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        if AnonymousUserStatusInSurveys.objects.all():
            anonymous_id = AnonymousUserAnswer.objects.aggregate(Max('id'))
            anonymous_id['id'] += 1
        else:
            anonymous_id = {'id': 1}
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data.update(anonymous_id)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CreateUserAnswerCreateAPIView(CreateAPIView):
    """Use this request to send answers to questions as authorized user.

    You cannot use this request for anonymous, use /api/survey/<int:pk>/answer/anonymous/ instead

    Actually, you don't need to send "survey" and "user", server added this fields automatically."""

    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if not user or not user.is_active:
            raise NotAuthenticated('This POST request method allowed only for registered users. ' +
                                   'For anonymous use api/survey/<int:pk>/answer/anonymous')
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        data = request.data
        if not data.get('survey'):
            data.update({'survey': (survey.id, )})
        if not data.get('user'):
            data.update({'user': user.id})
        if data.get('question'):
            question_type = get_object_or_404(Question, pk=data.get('question')).type.id
            if question_type == 1 and data.get('answer_choose'):
                raise ParseError('Invalid "answer_choose" for question type "Text". This field should be empty.')
            if question_type == 2 and data.get('answer_text'):
                raise ParseError('Invalid "answer_text" for question type "Radio". This field should be empty.')
            if question_type == 2 and len(data.get('answer_choose')) > 1:
                raise ParseError('Invalid "answer_choose" for question type "Radio". This field should have 1 value.')
            if question_type == 3 and data.get('answer_text'):
                raise ParseError('Invalid "answer_text" for question type "Checkbox". This field should be empty.')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CompleteSurveyUpdateAPIView(UpdateAPIView):
    """Use this request to complete survey for authorized user.

    You cannot use this request for anonymous, use /api/survey/<int:pk>/complete/anonymous/ instead.

    Actually, you don't need to send anything, server set status as complete anyway.

    Remember, that you cannot complete survey if you don't start it, or you send not enough answers.

    WARNING: PUT request works as PATCH."""
    serializer_class = CompleteSurveySerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_active:
            raise NotAuthenticated('This POST request method allowed only for registered users. ' +
                                   'For anonymous use api/survey/<int:pk>/complete/anonymous')
        return UserStatusInSurveys.objects.filter(user=user.id)

    def update(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        user = request.user
        if not user or not user.is_active:
            raise NotAuthenticated('This POST request method allowed only for registered users. ' +
                                   'For anonymous use api/survey/<int:pk>/complete/anonymous')
        user_status_in_survey = UserStatusInSurveys.objects.filter(user=user.id, survey=self.kwargs['pk'])
        if not user_status_in_survey:
            return Response({'user': 'This user not started this survey'}, status=status.HTTP_400_BAD_REQUEST)
        if user_status_in_survey[0].completed:
            return Response({'user': 'This user already completed this survey'}, status=status.HTTP_400_BAD_REQUEST)
        answered_questions = UserAnswer.objects.filter(user=user.id).count()
        questions = survey.questions.all().count()
        if answered_questions != questions:
            return Response({'user': 'This user not answered to all questions.'}, status=status.HTTP_400_BAD_REQUEST)
        user_status = UserStatusInSurveys.objects.get(user=user.id)
        serializer = self.get_serializer(user_status, data={'completed': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


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
