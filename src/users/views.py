from django.contrib import auth
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError
from rest_framework.permissions import IsAuthenticated

from surveys.serializes import SurveyActiveSerializer, SurveyCompletedSerializer
from surveys.models import Survey
from users.models import UserStatusInSurveys, UserAnswer
from users.serializes import UserRegistrationSerializer, UserAnswerShortSerializer, UserLoginSerializer, PlugSerializer


class ActiveSurveysListAPIView(ListAPIView):
    """Returns list of active surveys for this user.

    Allows only for registered user."""
    permission_classes = (IsAuthenticated, )
    serializer_class = SurveyActiveSerializer

    def get_queryset(self):
        active_surveys = UserStatusInSurveys.objects.filter(user=self.request.user.id, completed=False)
        if active_surveys:
            active_surveys = active_surveys.values_list('survey', flat=True)
            return Survey.objects.filter(id__in=active_surveys)
        else:
            raise NotFound(detail='Not founded any active survey for this user')


class CompletedSurveysListAPIView(ListAPIView):
    """Returns list of completed surveys for this user.

    Allows only for registered user."""
    permission_classes = (IsAuthenticated, )
    serializer_class = SurveyCompletedSerializer

    def get_queryset(self):
        completed_surveys = UserStatusInSurveys.objects.filter(user=self.request.user.id, completed=True)
        if completed_surveys:
            completed_surveys = completed_surveys.values_list('survey', flat=True)
            return Survey.objects.filter(id__in=completed_surveys)
        else:
            raise NotFound(detail='Not founded any completed survey for this user')


class UserAnswersListAPIView(ListAPIView):
    """Returns list of answers to questions for concrete survey (using id).

    Allows only for registered user."""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserAnswerShortSerializer

    def get_queryset(self):
        survey = Survey.objects.filter(id=self.kwargs['pk'])
        if survey:
            answers = UserAnswer.objects.filter(user=self.request.user.id, survey=self.kwargs['pk'])
            if answers:
                return answers
            else:
                raise NotFound(detail='Answers not found in this survey for this user.')
        else:
            raise NotFound(detail='Survey not found.')


class UserCreateAPIView(CreateAPIView):
    """Use this request to registrate new user.

    Remember that you cannot register if you are already signed in."""
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        if self.request.user.is_active:
            raise ParseError(detail='You trying to register user when you already authenticated.')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LoginAPIView(CreateAPIView):
    """Use this request for login."""
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return Response({'username': username, 'password': password}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error_message': 'Login or password is incorrect.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            not_founded_fields = [field for field in ('username', 'password') if not request.data.get(field)]
            return Response({val: 'required' for val in not_founded_fields}, status=status.HTTP_400_BAD_REQUEST)


class LogoutRetrieveAPIView(RetrieveAPIView):
    """Use this request for logout."""
    serializer_class = PlugSerializer

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth.logout(request)
            return Response({'username': request.user.username + 'logout'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'user': 'not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
