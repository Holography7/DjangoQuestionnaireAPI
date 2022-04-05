from django.urls import path

from surveys.views import api_complete_survey, SurveyAPIView, SurveyListAPIView, QuestionsListAPIView, CompleteSurveyUpdateAPIView
from surveys.views import StartSurveyCreateAPIView, StartSurveyAsAnonymousCreateAPIView, CreateUserAnswerCreateAPIView

app_name = 'survey'

urlpatterns = [
    path('list/', SurveyListAPIView.as_view(), name='api_surveys_list'),
    path('<int:pk>/', SurveyAPIView.as_view(), name='api_survey'),
    path('<int:pk>/start', StartSurveyCreateAPIView.as_view(), name='api_survey_start'),
    path('<int:pk>/start/anonymous', StartSurveyAsAnonymousCreateAPIView.as_view(), name='api_survey_start_anonymous'),
    path('<int:pk>/answer', CreateUserAnswerCreateAPIView.as_view(), name='api_survey_answer'),
    path('<int:pk>/questions/', QuestionsListAPIView.as_view(), name='api_questions'),
    path('<int:pk>/complete/old', api_complete_survey, name='api_complete_survey_old'),
    path('<int:pk>/complete', CompleteSurveyUpdateAPIView.as_view(), name='api_complete_survey'),
]
