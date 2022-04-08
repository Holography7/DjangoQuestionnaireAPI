from django.urls import path

from surveys.views import SurveyListAPIView, QuestionsListAPIView, CompleteSurveyAsAnonymousUpdateAPIView
from surveys.views import StartSurveyCreateAPIView, StartSurveyAsAnonymousCreateAPIView, CreateUserAnswerCreateAPIView
from surveys.views import CreateAnonymousUserAnswerCreateAPIView, CompleteSurveyUpdateAPIView

app_name = 'survey'

urlpatterns = [
    path('list/', SurveyListAPIView.as_view(), name='api_surveys_list'),
    path('<int:pk>/start', StartSurveyCreateAPIView.as_view(), name='api_survey_start'),
    path('<int:pk>/start/anonymous', StartSurveyAsAnonymousCreateAPIView.as_view(), name='api_survey_start_anonymous'),
    path('<int:pk>/answer', CreateUserAnswerCreateAPIView.as_view(), name='api_survey_answer'),
    path('<int:pk>/answer/anonymous', CreateAnonymousUserAnswerCreateAPIView.as_view(),
         name='api_survey_answer_anonymous'),
    path('<int:pk>/questions/', QuestionsListAPIView.as_view(), name='api_questions'),
    path('<int:pk>/complete', CompleteSurveyUpdateAPIView.as_view(), name='api_complete_survey'),
    path('<int:pk>/complete/anonymous', CompleteSurveyAsAnonymousUpdateAPIView.as_view(),
         name='api_complete_survey_anonymous'),
]
