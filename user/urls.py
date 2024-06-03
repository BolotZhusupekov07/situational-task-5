from django.urls import path

from user import views


urlpatterns = [
    path('auth/google/authorization_url/', views.GoogleAuthorizationURLAPI.as_view()),
    path('auth/google/callback/', views.GoogleAuthAPI.as_view()),
]