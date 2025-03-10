import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Bet, Match

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Password must be between 8 and 20 characters
        if not (8 <= len(password) <= 20):
            raise ValidationError("Password must be between 8 and 20 characters long.")

        # Require at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        # Require at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")

        # Require at least one digit
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")

        # Require at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

class MatchSelectWidget(forms.Select):
    """ Custom Select widget to add team1 and team2 as data attributes dynamically. """
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        # Extract actual value if it's a ModelChoiceIteratorValue
        match_id = getattr(value, "value", value)

        # Ensure value is a valid match ID (avoid None or empty selections)
        if match_id:
            try:
                match = Match.objects.get(pk=match_id)  # Get match instance
                option["attrs"]["data-team1"] = match.team1
                option["attrs"]["data-team2"] = match.team2
                option["attrs"]["data-odds-team1"] = match.odds_team1
                option["attrs"]["data-odds-team2"] = match.odds_team2
            except Match.DoesNotExist:
                pass  # Prevent errors if match is missing

        return option

class CreateBetForm(forms.ModelForm):
    user_2 = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.TextInput(attrs={
            "placeholder": "Search for opponent by username or ID",
            "id": "user_search"
        }),
        required=True
    )

    bet_match = forms.ModelChoiceField(
        queryset=Match.objects.filter(match_status="upcoming"),
        empty_label="Select a match",
        widget=MatchSelectWidget(attrs={"class": "form-control"}),  # Custom widget to store match teams
    )

    bet_choice = forms.ChoiceField(choices=[], required=True)

    selected_odd = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        widget=forms.NumberInput(attrs={"step": "0.01"})
    )

    class Meta:
        model = Bet
        fields = ["user_2", "bet_match", "bet_choice", "amount_user_1", "amount_user_2", "selected_odd"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bet_choice"].widget = forms.Select(attrs={"class": "form-control"})

        # Dynamically populate choices
        if "bet_match" in self.data:
            match_id = self.data["bet_match"]
            try:
                match = Match.objects.get(id=match_id)
                self.fields["bet_choice"].choices = [
                    (match.team1, f"{match.team1} (Odds: {match.odds_team1})"),
                    (match.team2, f"{match.team2} (Odds: {match.odds_team2})"),
                ]
            except Match.DoesNotExist:
                self.fields["bet_choice"].choices = []

    def clean(self):
        cleaned_data = super().clean()
        selected_odd = cleaned_data.get("selected_odd")
        bet_choice = cleaned_data.get("bet_choice")
        bet_match = cleaned_data.get("bet_match")

        if not selected_odd:
            raise forms.ValidationError("Selected odd must be provided.")

        # Validate bet_choice is one of the two teams
        if bet_match and bet_choice not in [bet_match.team1, bet_match.team2]:
            raise forms.ValidationError("Invalid bet choice. Must be one of the teams in the match.")

        return cleaned_data