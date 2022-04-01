from django.urls import path

from surveys.views import api_surveys_list, api_survey, api_question, api_complete_survey

app_name = 'survey'

urlpatterns = [
    path('api/surveys/', api_surveys_list, name='api_surveys_list'),
    path('api/surveys/<int:pk>', api_survey, name='api_survey'),
    path('api/surveys/<int:pk_survey>/<int:pk_question>', api_question, name='api_question'),
    path('api/surveys/<int:pk>/complete', api_complete_survey, name='api_complete_survey'),
]