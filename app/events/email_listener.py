from external_messaging.email import send_email
from .event import subscribe


def handle_game_found_event(email: str):
    send_email(address=email, subject="[LoL AFK Buddy] Game Found!", body="You are now in champion select.")

# TODO: possible events: pick, bans, game start


def setup_email_event_handlers():
    subscribe("game_found", handle_game_found_event)
