from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, CreateBetForm
from .models import Bet, Match
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@csrf_protect
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("matches")

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])  # Hash password
            user.save()
            login(request, user)  # Auto-login after signup
            return redirect("dashboard")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

@login_required
def dashboard(request):
    user = request.user

    # Fetch all bets and categorize them
    all_bets = Bet.objects.all()

    # Function to prepare dynamic fields
    def prepare_bet(bet, user):
        return {
            "id": bet.id,
            "bet_match": bet.bet_match,
            "bet_choice": bet.bet_choice,
            "opponent": bet.user_1 if bet.user_2 == user else bet.user_2,
            "your_amount": bet.amount_user_1 if bet.user_1 == user else bet.amount_user_2,
            "jackpot": round((bet.amount_user_1 + bet.amount_user_2) * Decimal('0.98'), 2),
            "status": bet.status,
            "created_at": bet.created_at,
        }

    current_bets = [prepare_bet(bet, user) for bet in all_bets.filter(status="in_progress")]
    awaiting_your_approval = [prepare_bet(bet, user) for bet in all_bets.filter(status="pending", user_2=user)]
    awaiting_opponent_approval = [prepare_bet(bet, user) for bet in all_bets.filter(status="pending", user_1=user)]
    past_bets = [prepare_bet(bet, user) for bet in all_bets.filter(status="processed")]

    # Pass categorized bets to the template
    context = {
        "user": user,
        "current_bets": current_bets,
        "awaiting_your_approval": awaiting_your_approval,
        "awaiting_opponent_approval": awaiting_opponent_approval,
        "past_bets": past_bets,
    }
    return render(request, "dashboard/dashboard.html", context)


def create_bet(request):
    if request.method == "POST":
        form = CreateBetForm(request.POST)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user_1 = request.user  # Ensure user is assigned
            bet.save()
            return redirect("dashboard")
        else:
            print(form.errors)  # Debugging - Shows validation errors in the console

    else:
        form = CreateBetForm()
    
    return render(request, "dashboard/create_bet.html", {"form": form})

@login_required
def accept_bet(request, bet_id):
    """Allows user_2 to accept, decline, or propose changes by swapping values and redirecting to create a new bet."""
    bet = get_object_or_404(Bet, id=bet_id)

    if request.user != bet.user_2:
        return redirect("dashboard")  # Only user_2 can act on this bet

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            bet.status = "in_progress"
            bet.save()
            return redirect("dashboard")

        elif action == "decline":
            bet.status = "invalidated"
            bet.save()
            return redirect("dashboard")

        elif action == "propose_changes":
            bet.status = "invalidated"
            bet.save()
            
            # Swap user_1 and user_2
            new_user_1 = bet.user_2
            new_user_2 = bet.user_1

            # Swap teams and odds from the **Match model**
            match = bet.bet_match
            new_bet_choice = match.team2 if bet.bet_choice == match.team1 else match.team1
            new_selected_odd = match.odds_team2 if bet.bet_choice == match.team1 else match.odds_team1

            # Swap bet amounts
            new_amount_user_1 = bet.amount_user_2
            new_amount_user_2 = bet.amount_user_1

            # Redirect to create_bet page with **reversed** values
            return redirect(
                f"{request.build_absolute_uri('/create_bet/')}?"
                f"bet_match={match.id}&bet_choice={new_bet_choice}"
                f"&amount_user_1={new_amount_user_1}&amount_user_2={new_amount_user_2}"
                f"&selected_odd={new_selected_odd}"
                f"&user_2={new_user_2.id}"
            )

    return render(request, "dashboard/accept_bet.html", {"bet": bet})


def matches(request):
    matches = Match.objects.all()  # Fetch all matches
    # group in matches happening right now, soon and recently completed matches
    current_matches = matches.filter(match_status="in_progress")
    upcoming_matches = matches.filter(match_status="upcoming")
    recent_matches = matches.filter(match_status="completed")
    return render(request, 'matches/matches.html', {'current_matches': current_matches, 'upcoming_matches': upcoming_matches, 'recent_matches': recent_matches})