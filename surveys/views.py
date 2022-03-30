from django.shortcuts import get_object_or_404, render
from datetime import datetime

from surveys.models import Survey


def survey_view(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    if survey:
        questions = survey.questions.all()
        survey_outdated = survey.date_end.timestamp() < datetime.now().timestamp()
    else:
        questions = []
        survey_outdated = None
    context = {'survey': survey, 'questions': questions,
               'survey_outdated': survey_outdated}
    return render(request, 'surveys/survey.html', context)
