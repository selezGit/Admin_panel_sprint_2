from django.urls import include, path

from .v1 import views

urlpatterns = [
    path('v1/', include('movie_admin.api.v1.urls')),
    path('movies/<uuid:pk>/', views.MoviesDetailApi.as_view()),
]
