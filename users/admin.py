from django.contrib import admin

from users.models import User, UserAnswer, AnonymousUserAnswer

admin.site.register(User)
admin.site.register(UserAnswer)
admin.site.register(AnonymousUserAnswer)
