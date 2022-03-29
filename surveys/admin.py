from django.contrib import admin

from surveys.models import Survey, AnswersVariants, Question, QuestionType

admin.site.register(AnswersVariants)
admin.site.register(QuestionType)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_start', 'date_end')
	fields = ('name', 'date_end', 'description', 'questions')
	ordering = ('name',)
	search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('question', 'type')
	# fields = ('question', 'type', 'answers.answer')
	ordering = ('question',)
	search_fields = ('question',)
