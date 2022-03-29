from django.shortcuts import render


def profile(request):
    return render(request, 'users/profile.html')


def registration(request):
    return render(request, 'users/registration.html')
