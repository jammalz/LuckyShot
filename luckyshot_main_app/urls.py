from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_bet/', views.create_bet, name='create_bet'),
    path("bet/<int:bet_id>/accept/", views.accept_bet, name="accept_bet"),
    path("matches/", views.matches, name="matches"),
    path("", views.matches, name="matches"),
]