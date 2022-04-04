"""questionnaire URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('survey/', include('surveys.urls', namespace='survey')),
    path('user/', include('users.urls', namespace='users')),
    path('openapi/', get_schema_view(
        title="Questionnaire API",
        description="API for developers who wants do questionnaire",
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='surveys/documentation.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]
