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
    path("stripe/deposit/", views.create_checkout_session, name="stripe_deposit"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("bet/<int:bet_id>/settle/", views.settle_bet, name="settle_bet"),
]