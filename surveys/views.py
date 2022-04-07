from datetime import datetime
import pytz
from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.exceptions import PermissionDenied, ParseError, NotAuthenticated
from rest_framework.permissions import IsAuthenticated


from surveys.models import Survey, Question
from surveys.serializes import SurveySerializer, QuestionSerializer
from users.models import UserAnswer, AnonymousUserAnswer, UserStatusInSurveys, AnonymousUserStatusInSurveys
from users.serializes import UserAnswerSerializer, AnonymousUserAnswerSerializer, UserStatusInSurveysSerializer
from users.serializes import AnonymousUserStatusInSurveysSerializer, CompleteSurveySerializer
from users.serializes import CompleteSurveyAsAnonymousSerializer


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
    start survey or already complete this survey.

    You should send anonymous_id in cookie to get access as anonymous user. You can get it when you send POST to
    api/survey/<int:id>/start/anonymous for the first time."""
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
            return survey.questions.all()
        else:
            if 'anonymous_id' not in self.request.COOKIES:
                raise PermissionDenied(detail='This anonymous user not have anonymous_id in cookie.')
            anonymous_id = self.request.COOKIES['anonymous_id']
            anonymous_status = AnonymousUserStatusInSurveys.objects.filter(user_anonymous_id=anonymous_id,
                                                                           survey=survey.id)
            if not anonymous_status:
                raise PermissionDenied(detail="This anonymous user didn't start this survey")
            if anonymous_status[0].completed:
                raise PermissionDenied(detail='This anonymous user already complete this survey')
            return survey.questions.all()


class StartSurveyCreateAPIView(CreateAPIView):
    """Use this request to start survey as authenticated user.

    You cannot use this method as anonymous, use /api/survey/<int:pk>/start/anonymous/ instead.

    You don't need to send anything in POST, server can grab this fields by itself."""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserStatusInSurveysSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not data.get('survey'):
            data.update({'survey': [self.kwargs['pk']]})
        if not data.get('user'):
            data.update({'user': [request.user.id]})
        else:
            if data['user'] != request.user.id:
                raise ParseError(detail='user value not same as from request.')
        survey = get_object_or_404(Survey, pk=data['survey'][0])
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        if UserStatusInSurveys.objects.filter(user=request.user.id, survey=survey.id):
            raise ParseError(detail='This user already start or complete this survey.')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StartSurveyAsAnonymousCreateAPIView(CreateAPIView):
    """Use this request to start survey as anonymous user.

    You cannot use this method as authenticated user, use /api/survey/<int:pk>/start/ instead.

    Don't forget that server using cookies for anonymous. anonymous_id is creating there."""
    serializer_class = AnonymousUserStatusInSurveysSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not data.get('survey'):
            data.update({'survey': [self.kwargs['pk']]})
        survey = get_object_or_404(Survey, pk=data['survey'][0])
        if 'anonymous_id' in request.COOKIES:
            anonymous_id = request.COOKIES['anonymous_id']
            anonymous_status = AnonymousUserStatusInSurveys.objects.filter(user_anonymous_id=anonymous_id,
                                                                           survey=survey.id)
            if anonymous_status:
                raise ParseError('This anonymous already start or complete this survey')
            if not data.get('user_anonymous_id'):
                data.update({'user_anonymous_id': anonymous_id})
            else:
                if data.get('user_anonymous_id') != anonymous_id:
                    raise ParseError(detail='user_anonymous_id value not same as from cookie.')
        else:
            anonymous_id = None
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        if not anonymous_id:
            if AnonymousUserStatusInSurveys.objects.all():
                anonymous_id = AnonymousUserStatusInSurveys.objects.aggregate(Max('id'))
                anonymous_id['id__max'] += 1
            else:
                anonymous_id = {'id__max': 1}
        else:
            anonymous_id = {'id__max': anonymous_id}
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        if 'anonymous_id' not in request.COOKIES:
            max_age = survey.date_end.timestamp() - pytz.UTC.localize(datetime.now()).timestamp()
            response.set_cookie('anonymous_id', anonymous_id['id__max'], max_age=max_age)
        return response


class CreateUserAnswerCreateAPIView(CreateAPIView):
    """Use this request to send answers to questions as authorized user.

    You cannot use this request for anonymous, use /api/survey/<int:pk>/answer/anonymous/ instead

    Actually, you don't need to send "survey" and "user", server added this fields automatically.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not data.get('survey'):
            data.update({'survey': [self.kwargs['pk']]})
        if not data.get('user'):
            data.update({'user': request.user.id})
        else:
            if data['user'] != request.user.id:
                raise ParseError(detail='user value not same as from request.')
        survey = get_object_or_404(Survey, pk=data['survey'][0])
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        question = get_object_or_404(Question, pk=data.get('question'))
        if question not in survey.questions.all():
            raise ParseError('Question not in this survey.')
        answer = UserAnswer.objects.filter(id=request.user.id, survey=survey.id, question=question.id)
        if answer:
            raise ParseError('This user already created answer.')
        validate_answer(question, data.get('answer_text'), data.get('answer_choose'))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CreateAnonymousUserAnswerCreateAPIView(CreateAPIView):
    """Use this request to send answers to questions as anonymous user.

    You cannot use this request for authorized, use /api/survey/<int:pk>/answer/ instead.

    Remember that "anonymous_id" should be sent as cookie, without this value you will get 401 response.

    Actually, you don't need to send "survey" and "user_anonymous_id", server added this fields automatically."""
    serializer_class = AnonymousUserAnswerSerializer

    def create(self, request, *args, **kwargs):
        if 'anonymous_id' in request.COOKIES:
            anonymous_id = request.COOKIES['anonymous_id']
        else:
            raise NotAuthenticated('This POST request required "anonymous_id" in cookies.')
        if self.request.user and self.request.user.is_active:
            raise NotAuthenticated('This POST request method allowed only for anonymous users. ' +
                                   'For authorized users use api/survey/<int:pk>/answer/')
        data = request.data
        if not data.get('survey'):
            data.update({'survey': [self.kwargs['pk']]})
        if not data.get('user_anonymous_id'):
            data.update({'user_anonymous_id': anonymous_id})
        else:
            if data.get('user_anonymous_id') != anonymous_id:
                raise ParseError(detail='user_anonymous_id value not same as from cookie.')
        survey = get_object_or_404(Survey, pk=data['survey'][0])
        question = get_object_or_404(Question, pk=data.get('question'))
        if question not in survey.questions.all():
            raise ParseError('Question not in this survey.')
        answer = AnonymousUserAnswer.objects.filter(user_anonymous_id=anonymous_id, survey=survey.id, question=question.id)
        if answer:
            raise ParseError('This anonymous user already created answer.')
        if survey.date_end < pytz.UTC.localize(datetime.now()):
            raise PermissionDenied(detail='This survey is outdated')
        validate_answer(question, data.get('answer_text'), data.get('answer_choose'))
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
    permission_classes = (IsAuthenticated,)
    serializer_class = CompleteSurveySerializer

    def get_queryset(self):
        return UserStatusInSurveys.objects.filter(user=self.request.user.id)

    def update(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        user_status_in_survey = UserStatusInSurveys.objects.filter(user=request.user.id, survey=self.kwargs['pk'])
        if not user_status_in_survey:
            return Response({'user': 'This user not started this survey'}, status=status.HTTP_400_BAD_REQUEST)
        if user_status_in_survey[0].completed:
            return Response({'user': 'This user already completed this survey'}, status=status.HTTP_400_BAD_REQUEST)
        answered_questions = UserAnswer.objects.filter(user=request.user.id).count()
        questions = survey.questions.all().count()
        if answered_questions != questions:
            return Response({'user': 'This user not answered to all questions.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user_status_in_survey[0], data={'completed': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CompleteSurveyAsAnonymousUpdateAPIView(UpdateAPIView):
    """Use this request to complete survey for anonymous user.

    You cannot use this request for authorized user, use /api/survey/<int:pk>/complete/ instead.

    Actually, you don't need to send anything, server set status as complete anyway.

    Remember, that you cannot complete survey if you don't start it, or you send not enough answers.

    WARNING: PUT request works as PATCH."""
    serializer_class = CompleteSurveyAsAnonymousSerializer

    def get_queryset(self):
        if 'anonymous_id' in self.request.COOKIES:
            anonymous_id = self.request.COOKIES['anonymous_id']
        else:
            raise NotAuthenticated('This request required "anonymous_id" in cookies.')
        if self.request.user and self.request.user.is_active:
            raise NotAuthenticated('This request method allowed only for anonymous users. ' +
                                   'For authorized users use api/survey/<int:pk>/complete/')
        return AnonymousUserStatusInSurveys.objects.filter(user_anonymous_id=anonymous_id)

    def update(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if 'anonymous_id' in self.request.COOKIES:
            anonymous_id = self.request.COOKIES['anonymous_id']
        else:
            raise NotAuthenticated('This request required "anonymous_id" in cookies.')
        if self.request.user and self.request.user.is_active:
            raise NotAuthenticated('This request method allowed only for anonymous users. ' +
                                   'For authorized users use api/survey/<int:pk>/complete/')
        anonymous_user_status_in_survey = AnonymousUserStatusInSurveys.objects.filter(user_anonymous_id=anonymous_id,
                                                                                      survey=self.kwargs['pk'])
        if not anonymous_user_status_in_survey:
            return Response({'user': 'This anonymous user not started this survey'}, status=status.HTTP_400_BAD_REQUEST)
        if anonymous_user_status_in_survey[0].completed:
            return Response({'user': 'This anonymous user already completed this survey'},
                            status=status.HTTP_400_BAD_REQUEST)
        answered_questions = AnonymousUserAnswer.objects.filter(user_anonymous_id=anonymous_id).count()
        questions = survey.questions.all().count()
        if answered_questions != questions:
            return Response({'user': 'This anonymous user not answered to all questions.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(anonymous_user_status_in_survey[0], data={'completed': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


def validate_answer(question, answer_text, answer_choose):
    question_type = question.type.type
    if question_type == 'Text' and answer_choose:
        raise ParseError('Invalid "answer_choose" for question type "Text". This field should be empty.')
    if question_type == 'Radio' and answer_text:
        raise ParseError('Invalid "answer_text" for question type "Radio". This field should be empty.')
    if question_type == 'Radio' and len(answer_choose) > 1:
        raise ParseError('Invalid "answer_choose" for question type "Radio". This field should have 1 value.')
    if question_type == 'Checkbox' and answer_text:
        raise ParseError('Invalid "answer_text" for question type "Checkbox". This field should be empty.')
    if question_type != 'Text':
        answers_variants = question.answers.all().values('id')
        for answer_request in answer_choose:
            if {'id': answer_request} not in answers_variants:
                raise ParseError('Invalid "answer_choose": answer not in this question.')
