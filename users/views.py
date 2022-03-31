from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from surveys.serializes import SurveySerializer
from users.forms import UserRegistrationForm
from users.models import User
from users.serializes import UserSerializer


@login_required
def profile(request):
    return render(request, 'users/profile.html')


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:login'))
        else:
            context = {'error_messages': form.errors}
            return render(request, 'users/registration.html', context)
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:profile'))
        return render(request, 'users/registration.html')


def user_answers(request, survey_id):
    return render(request, 'users/user_answers.html')


@api_view(['POST'])
def api_registration(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return Response({"user_is_authenticated": True}, status=status.HTTP_208_ALREADY_REPORTED)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_completed_surveys(request):
    if request.method == 'GET':
        surveys = User.objects.get(id=request.user.id).completed_surveys
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def api_login(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return Response({"user_is_authenticated": True}, status=status.HTTP_208_ALREADY_REPORTED)
        username = request.data['username']
        password = request.data['password']
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            return Response({"user_is_authenticated": True}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error_message': "Login or password is incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_logout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            auth.logout(request)
            return Response({"user_logouted": True}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"user_not_login": True}, status=status.HTTP_400_BAD_REQUEST)
