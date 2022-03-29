from django.urls import path

from users.views import profile, registration

app_name = 'users'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('registration/', registration, name='registration'),
]