from django.urls import path

from users.views import profile, registration, user_answers, api_completed_surveys, api_login, api_logout, api_registration

app_name = 'users'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('registration/', registration, name='registration'),
    path('surveys/<int:survey_id>', user_answers, name='user_answers'),
    path('api/surveys/', api_completed_surveys, name='api_completed_surveys'),
    path('api/login/', api_login, name='api_login'),
    path('api/logout/', api_logout, name='api_logout'),
    path('api/registration/', api_registration, name='api_registration'),
]
