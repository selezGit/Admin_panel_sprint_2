# pylint: disable=import-error

from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^movies/(?:page=(?P<page>\d+)/)?$', views.MoviesListApi.as_view()),
    path('movies/<uuid:pk>/', views.MoviesDetailApi.as_view())
]