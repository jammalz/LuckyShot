from django.contrib import admin
from .models import Bet, Match, Transaction, UserBalance

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display =  ('user_1', 'user_2', 'bet_match', 'amount_user_1', 'amount_user_2', 'selected_odd', 'status', 'created_at', 'processed_at')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'start_time', 'match_status', 'odds_team1', 'odds_team2', 'score_team1', 'score_team2', 'last_updated')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet', 'transaction_type', 'amount', 'stripe_payment_id', 'status', 'created_at')

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'available_balance', 'reserved_balance')