from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movies),
    path('comments/', views.comments),
    path('top/', views.top)
]
