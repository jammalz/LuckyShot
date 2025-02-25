from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bet(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("processed", "Processed"),
    ]

    BET_TYPES = [
        ("match_winner", "Match Winner"),
    ]

    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bets_created")
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bets_received")
    bet_match = models.ForeignKey("Match", on_delete=models.CASCADE)
    bet_type = models.CharField(max_length=50, choices=BET_TYPES, default="match_winner")
    bet_choice = models.CharField(max_length=50)
    amount_user_1 = models.DecimalField(max_digits=10, decimal_places=2)
    amount_user_2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selected_odd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_bets")

    # def calculate_odd(self):
    #     """Automatically calculates odds based on user bet amounts if one is missing."""
    #     if self.amount_user_1 and self.amount_user_2:
    #         return round(self.amount_user_2 / self.amount_user_1, 2)
    #     return None

    def save(self, *args, **kwargs):
        """Ensure odds are updated before saving."""
        if not self.selected_odd and self.amount_user_1 and self.amount_user_2:
            self.selected_odd = self.calculate_odd()

        # Auto-validate bet_choice to be one of the teams in bet_match
        if self.bet_match and self.bet_choice:
            teams = [self.bet_match.team1, self.bet_match.team2]
            if self.bet_choice not in teams:
                raise ValueError(f"Invalid bet choice. Must be one of {teams}")
        
        super().save(*args, **kwargs)

    def mark_processed(self, winner):
        """Mark the bet as processed and assign the winner"""
        self.status = "processed"
        self.winner = winner
        self.processed_at = timezone.now()
        self.save()

    def __str__(self):
        # if current user is user_2, show user_1 as the opponent and the other choice as the bet_choice
        current_user = User.objects.get(username="current_user")
        if self.user_2 == current_user:
            opponent = self.user_1
            bet_choice = self.bet_match.split(" vs ")[0] if self.bet_choice == self.bet_match.split(" vs ")[1] else self.bet_match.split(" vs ")[1]
        else:
            opponent = self.user_2
            bet_choice = self.bet_choice
        return f"Bet: {current_user} vs {opponent} - {self.bet_match} - Your choice: {bet_choice}"
    
class Match(models.Model):
    external_id = models.CharField(max_length=100, unique=True)  # API Match ID
    league_id = models.IntegerField(default=475)  # Paulista A1
    team1 = models.CharField(max_length=100)
    team1_logo = models.URLField(null=True, blank=True)
    team2 = models.CharField(max_length=100)
    team2_logo = models.URLField(null=True, blank=True)
    start_time = models.DateTimeField(db_index=True)

    # Betting Odds
    odds_team1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    odds_team2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Live Updates
    score_team1 = models.IntegerField(null=True, blank=True, default=0)
    score_team2 = models.IntegerField(null=True, blank=True, default=0)
    match_status = models.CharField(
        max_length=20,
        choices=[("upcoming", "Upcoming"), ("live", "Live"), ("finished", "Finished"), ("canceled", "Canceled")],
        default="upcoming",
    )
    last_updated = models.DateTimeField(auto_now=True)  # Track updates

    def is_live(self):
        return self.match_status == "live"

    def __str__(self):
        start_time = self.start_time.strftime("%Y-%m-%d %H:%M")
        return f"{self.team1} vs {self.team2} - {start_time}"

    class Meta:
        ordering = ["start_time"]

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("bet_placed", "Bet Placed"),
        ("bet_won", "Winnings Paid"),
        ("bet_refunded", "Bet Refunded"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    bet = models.ForeignKey("Bet", null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)  # Store Stripe payment ID
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"
    

class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Usable funds
    reserved_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Locked in pending bets

    def total_balance(self):
        """ Total balance is the sum of available + reserved funds. """
        return self.available_balance + self.reserved_balance
