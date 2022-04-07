from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from users.views import ActiveSurveysListAPIView, CompletedSurveysListAPIView, UserAnswersListAPIView, UserCreateAPIView
from users.views import LoginAPIView, LogoutRetrieveAPIView

app_name = 'users'

urlpatterns = [
    path('auth/', obtain_auth_token, name='auth'),
    path('surveys/completed/', CompletedSurveysListAPIView.as_view(), name='api_completed_surveys'),
    path('surveys/answers/<int:pk>', UserAnswersListAPIView.as_view(), name='api_survey_answers'),
    path('surveys/active', ActiveSurveysListAPIView.as_view(), name='api_active_surveys'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('logout/', LogoutRetrieveAPIView.as_view(), name='api_logout'),
    path('registration/', UserCreateAPIView.as_view(), name='api_registration'),
]
