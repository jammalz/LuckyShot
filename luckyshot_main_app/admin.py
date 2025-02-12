from django.contrib import admin
from .models import Bet, Match

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display =  ('user_1', 'user_2', 'bet_match', 'amount_user_1', 'amount_user_2', 'selected_odd', 'status', 'created_at', 'processed_at')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'teams', 'odds', 'status')