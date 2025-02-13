import os
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v3.football.api-sports.io"

class APISportsClient:
    def __init__(self):
        self.headers = {"x-apisports-key": API_KEY}

    def get_upcoming_matches(self, league_id=475):
        """ Fetch upcoming matches for Paulista A1 2025 """
        url = f"{BASE_URL}/fixtures"
        params = {"league": league_id, "season": 2023, "team": 126, "from": "2023-02-05", "to": "2023-02-06"}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json().get("response", [])
        else:
            print(f"Error fetching matches: {response.status_code} - {response.text}")
            return []

    def get_odds(self, match_id):
        """ Fetch odds for a specific match """
        url = f"{BASE_URL}/odds"
        params = {"fixture": match_id, "bookmaker": 1}  # Example: Bookmaker ID 1
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json().get("response", [])
        else:
            print(f"Error fetching odds: {response.status_code} - {response.text}")
            return []
