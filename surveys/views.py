from django.shortcuts import render
from datetime import datetime

from surveys.models import Survey


def survey_view(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    if survey:
        questions = survey.questions.all()
    else:
        questions = []
    context = {'survey': survey, 'questions': questions,
               'survey_outdated': survey.date_end.timestamp() < datetime.now().timestamp()}
    return render(request, 'surveys/survey.html', context)
