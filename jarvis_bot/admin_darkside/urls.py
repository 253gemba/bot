from django.conf.urls import url
from django.contrib import admin
# from . import views
from django.urls import include, path

urlpatterns = [
    path('tinymce/', include('tinymce.urls')),
]
