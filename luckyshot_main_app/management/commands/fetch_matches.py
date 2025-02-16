from django.core.management.base import BaseCommand
from luckyshot_main_app.models import Match
from luckyshot_main_app.services.api_sports import APISportsClient
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
import random
import math


# Function to generate reasonable odds
def generate_fair_odds():
    # Generate a random odd for team 1 between 1.3 and 4.0,
    base_value = random.uniform(0.1, 1.0)
    odds_team1 = round(1.3 + (3.7 * math.pow(base_value, 2)), 2)
    
    # Calculate the implied probability for team 1
    prob_team1 = 1 / odds_team1
    
    # Calculate the fair odds for team 2
    odds_team2 = round(1 / (1 - prob_team1), 2)

    return odds_team1, odds_team2

class Command(BaseCommand):
    help = "Fetch upcoming matches for Paulista A1 2025"

    def handle(self, *args, **kwargs):
        api_client = APISportsClient()
        matches = api_client.get_upcoming_matches()

        for match in matches:
            match_id = match["fixture"]["id"]
            home_team = match["teams"]["home"]["name"]
            home_team_logo = match["teams"]["home"]["logo"]
            away_team = match["teams"]["away"]["name"]
            away_team_logo = match["teams"]["away"]["logo"]
            start_time = parse_datetime(match["fixture"]["date"])

            # Fetch odds
            odds_data = api_client.get_odds(match_id)
            # if cant find odds, randomize bet
            if odds_data and odds_data[0].get("odds"):
                odds_team1 = odds_data[0]["odds"]["home"]
                odds_team2 = odds_data[0]["odds"]["away"]
            else:
                odds_team1, odds_team2 = generate_fair_odds()

            # Store match in database
            match_obj, created = Match.objects.update_or_create(
                external_id=match_id,
                defaults={
                    "team1": home_team,
                    "team1_logo": home_team_logo,
                    "team2": away_team,
                    "team2_logo": away_team_logo,
                    "start_time": start_time,
                    "odds_team1": odds_team1,
                    "odds_team2": odds_team2,
                    "match_status": "upcoming",
                },
            )

            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status}: {home_team} vs {away_team}"))

