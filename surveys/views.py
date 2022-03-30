from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime

from surveys.models import Survey
from users.models import UserAnswer


def survey_view(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    if survey:
        questions = survey.questions.all()
        survey_outdated = survey.date_end.timestamp() < datetime.now().timestamp()
    else:
        questions = []
        survey_outdated = None
    context = {'survey': survey, 'questions': questions, 'survey_outdated': survey_outdated}
    return render(request, 'surveys/survey.html', context)


def question(request, survey_id, question_pos_in_survey):
    if request.method == 'POST':
        survey = Survey.objects.get(id=survey_id)
        user = request.user
        question = survey.questions.all()[question_pos_in_survey - 1]
        answer = request.POST['answer']
        if str(question.type) == 'Text':
            instance = UserAnswer.objects.create(
                user=user,
                user_anonymous=False,
                answer_text=answer
            )
        else:
            instance = UserAnswer.objects.create(
                user=user,
                user_anonymous=False
            )
            for ans in answer:
                instance.answer_choose.set(question.answers.filter(id=ans))
        instance.survey.set((survey,))
        instance.question.set((question,))
        if question_pos_in_survey == len(survey.questions.all()):
            return HttpResponseRedirect(reverse('survey:complete'))
        else:
            return HttpResponseRedirect(reverse('survey:question',
                                                kwargs={'survey_id': survey_id,
                                                        'question_pos_in_survey': question_pos_in_survey + 1}))
    else:
        survey = Survey.objects.get(id=survey_id)
        question = survey.questions.all()[question_pos_in_survey - 1]
        context = {'survey': survey, 'question': question,
                   'question_pos_in_survey': question_pos_in_survey}
        return render(request, 'surveys/question.html', context)


def surveys_list(request):
    context = {'survey_list': Survey.objects.filter(date_end__gt=datetime.now())}
    return render(request, 'surveys/survey_list.html', context)


def complete(request):
    return render(request, 'surveys/survey_completed.html')
