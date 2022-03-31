from django.urls import path

from surveys.views import question, api_surveys_list, api_survey, api_question

app_name = 'survey'

urlpatterns = [
    path('<int:survey_id>/<int:question_pos_in_survey>', question, name='question'),
    path('api/surveys/', api_surveys_list, name='api_surveys_list'),
    path('api/surveys/<int:pk>', api_survey, name='api_survey'),
    path('api/surveys/<int:pk_survey>/<int:pk_question>', api_question, name='api_question')
]