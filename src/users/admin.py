from django.contrib import admin

from users.models import User, UserAnswer, AnonymousUserAnswer, UserStatusInSurveys, AnonymousUserStatusInSurveys

admin.site.register(User)
admin.site.register(UserAnswer)
admin.site.register(AnonymousUserAnswer)
admin.site.register(UserStatusInSurveys)
admin.site.register(AnonymousUserStatusInSurveys)
