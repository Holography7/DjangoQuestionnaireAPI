from django.urls import path

from surveys.views import survey_view

app_name = 'survey'

urlpatterns = [
    path('<int:survey_id>', survey_view, name='survey'),
]