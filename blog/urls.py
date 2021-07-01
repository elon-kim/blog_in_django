from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.PostList.as_view()),
    path('', views.PostList.as_view()),
]