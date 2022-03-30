from django.urls import path

from users.views import profile, registration, login, logout, surveys_completed, user_answers

app_name = 'users'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('surveys/', surveys_completed, name='surveys_completed'),
    path('surveys/<int:survey_id>', user_answers, name='user_answers'),
]