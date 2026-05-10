from django.urls import path
from myApp import views

urlpatterns = [
    path('screenData/', views.screenData, name='screenData'),
    path('productList/', views.productList, name='productList'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('changePassword/', views.changePassword, name='changePassword'),
]
