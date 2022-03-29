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
               'datetime': datetime.now().strftime('%B %d, %Y, %I{} %p'.format(':%M' if datetime.now().minute else ''))}
    return render(request, 'surveys/survey.html', context)
