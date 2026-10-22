from django.urls import path

from . import views

urlpatterns = [
    path('', views.list_request, name='list_request'),
    path('requests/new/', views.create_request, name='create_request'),
    path('requests/<int:pk>/', views.view_request, name='view_request'),
    path('requests/<int:pk>/edit/', views.update_request, name='update_request'),
    path('requests/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('requests/filter/', views.filter_request, name='filter_request'),
]
