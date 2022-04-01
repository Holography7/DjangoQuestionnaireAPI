from django.urls import path

from users.views import api_completed_surveys, api_login, api_logout, api_registration, api_active_surveys
from users.views import api_survey_answers

app_name = 'users'

urlpatterns = [
    path('api/surveys/completed', api_completed_surveys, name='api_completed_surveys'),
    path('api/surveys/completed/<int:pk>', api_survey_answers, name='api_survey_answers'),
    path('api/surveys/active', api_active_surveys, name='api_active_surveys'),
    path('api/login/', api_login, name='api_login'),
    path('api/logout/', api_logout, name='api_logout'),
    path('api/registration/', api_registration, name='api_registration'),
]
