from django.contrib import admin

from surveys.models import Survey, AnswersVariants, Question

admin.site.register(AnswersVariants)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_start', 'date_end')
	fields = ('name', 'date_end', 'description', 'questions')
	ordering = ('name',)
	search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('question', 'type')
	ordering = ('question',)
	search_fields = ('question',)
