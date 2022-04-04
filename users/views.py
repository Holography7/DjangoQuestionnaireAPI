from django.contrib import auth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from surveys.serializes import SurveySerializer
from surveys.models import Survey
from users.models import UserStatusInSurveys, UserAnswer
from users.serializes import UserRegistrationSerializer, UserAnswerShortSerializer


@api_view(['GET'])
def api_active_surveys(request):
    """Returns list of active surveys for this user. Allows only for registered user."""
    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            active_surveys = UserStatusInSurveys.objects.filter(user=user.id, completed=False)
            if active_surveys:
                active_surveys = active_surveys.values_list('survey', flat=True)
                surveys = Survey.objects.filter(id__in=active_surveys)
                serializer = SurveySerializer(surveys, many=True)
                return Response(serializer.data)
            else:
                return Response({"user": "not founded any active survey"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"user": "not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def api_registration(request):
    """Use this POST request for user registration."""
    if request.method == 'POST':
        if request.user.is_authenticated:
            return Response({"user_is_authenticated": True}, status=status.HTTP_208_ALREADY_REPORTED)
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_completed_surveys(request):
    """Returns list of completed surveys for this user. Allows only for registered user."""
    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            completed_surveys = UserStatusInSurveys.objects.filter(user=user.id, completed=True)
            if completed_surveys:
                completed_surveys = completed_surveys.values_list('survey', flat=True)
                surveys = Survey.objects.filter(id__in=completed_surveys)
                serializer = SurveySerializer(surveys, many=True)
                return Response(serializer.data)
            else:
                return Response({"user": "not founded any completed survey"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"user": "not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def api_survey_answers(request, pk):
    """Returns list of answers to questions for concrete survey (using id). Allows only for registered user."""
    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            survey = UserStatusInSurveys.objects.filter(user=user.id, survey=pk, completed=True)
            if survey:
                survey = Survey.objects.get(id=pk)
                answers = UserAnswer.objects.filter(user=user.id, survey=survey.id)
                serializer = UserAnswerShortSerializer(answers, many=True)
                return Response(serializer.data)
            else:
                return Response({'user': 'this survey not completed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"user": "not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def api_login(request):
    """Use this POST request for login."""
    if request.method == 'POST':
        if request.user.is_authenticated:
            return Response({"user": "already authenticated"},
                            status=status.HTTP_208_ALREADY_REPORTED)
        username = request.data.get('username')
        password = request.data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            return Response(request.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error_message': "Login or password is incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_logout(request):
    """Use this POST request for logout. POST should be empty (but with user information)"""
    if request.method == 'POST':
        if request.user.is_authenticated:
            auth.logout(request)
            return Response({"user": "logouted"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"user": "not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
