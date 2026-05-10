from django.urls import path
from myApp import views
urlpatterns = [
    path('screenData/', views.screenData, name='screenData')
]