from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from users.views import ActiveSurveysListAPIView, CompletedSurveysListAPIView, UserAnswersListAPIView, UserCreateAPIView

app_name = 'users'

urlpatterns = [
    path('api/auth/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('surveys/completed/', CompletedSurveysListAPIView.as_view(), name='api_completed_surveys'),
    path('surveys/answers/<int:pk>', UserAnswersListAPIView.as_view(), name='api_survey_answers'),
    path('surveys/active', ActiveSurveysListAPIView.as_view(), name='api_active_surveys'),
    path('registration/', UserCreateAPIView.as_view(), name='api_registration'),
]
