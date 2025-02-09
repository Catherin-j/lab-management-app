from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-lab/', views.create_lab, name='create_lab'),
    path('create-assignment/<int:lab_id>/', views.create_assignment, name='create_assignment'),
    path('compile/<int:assignment_id>/', views.compile_code, name='compile_code'),
    path('submit/<int:assignment_id>/', views.submit_code, name='submit_code'),
    path('review/<int:assignment_id>/', views.review_submissions, name='review_submissions'),
]