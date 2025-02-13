from django.core.management.base import BaseCommand
from luckyshot_main_app.models import Match
from luckyshot_main_app.services.api_sports import APISportsClient
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = "Fetch upcoming matches for Paulista A1 2025"

    def handle(self, *args, **kwargs):
        api_client = APISportsClient()
        matches = api_client.get_upcoming_matches()

        for match in matches:
            match_id = match["fixture"]["id"]
            home_team = match["teams"]["home"]["name"]
            away_team = match["teams"]["away"]["name"]
            start_time = parse_datetime(match["fixture"]["date"])

            # Fetch odds
            odds_data = api_client.get_odds(match_id)
            odds_team1 = odds_data[0]["odds"]["home"] if odds_data else None
            odds_team2 = odds_data[0]["odds"]["away"] if odds_data else None

            # Store match in database
            match_obj, created = Match.objects.update_or_create(
                external_id=match_id,
                defaults={
                    "team1": home_team,
                    "team2": away_team,
                    "start_time": start_time,
                    "odds_team1": odds_team1,
                    "odds_team2": odds_team2,
                    "match_status": "upcoming",
                },
            )

            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status}: {home_team} vs {away_team}"))

