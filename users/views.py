from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from users.forms import UserRegistrationForm
from users.models import User


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


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            context = {'error_message': "Login or password is incorrect."}
            return render(request, 'users/login.html', context)
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:profile'))
        return render(request, 'users/login.html')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('users:login'))


def surveys_completed(request):
    return render(request, 'users/surveys_completed.html')


def user_answers(request, survey_id):
    return render(request, 'users/user_answers.html')
