from django.urls import path

from surveys.views import survey_view, question, complete

app_name = 'survey'

urlpatterns = [
    path('<int:survey_id>', survey_view, name='survey'),
    path('<int:survey_id>/<int:question_pos_in_survey>', question, name='question'),
    path('completed/', complete, name='complete'),
]