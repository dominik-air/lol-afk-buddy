from typing import Dict
from external_messaging.email import send_email
from .event import subscribe


def handle_game_found_event(user_accounts: Dict[str, str]):
    email = user_accounts.get("email")
    if not email:
        return
    send_email(address=email, subject="[LoL AFK Buddy] Game Found!", body="You are now in champion select.")


def handle_champion_ban_event(user_accounts: Dict[str, str]):
    email = user_accounts.get("email")
    if not email:
        return
    send_email(address=email, subject="[LoL AFK Buddy] Champion Banned!", body="You are now in picking phase.")


def handle_champion_pick_event(user_accounts: Dict[str, str]):
    email = user_accounts.get("email")
    if not email:
        return
    send_email(address=email, subject="[LoL AFK Buddy] Champion Picked!", body="You are now in loadout phase.")


def handle_game_start_event(user_accounts: Dict[str, str]):
    email = user_accounts.get("email")
    if not email:
        return
    send_email(address=email, subject="[LoL AFK Buddy] The game has begun!", body="You are now in game.")


def setup_email_event_handlers():
    """Subscribe email events to event types here."""
    subscribe(event_type="game_found", function=handle_game_found_event)
    subscribe(event_type="champion_ban", function=handle_champion_ban_event)
    subscribe(event_type="champion_pick", function=handle_champion_pick_event)
    subscribe(event_type="game_start", function=handle_game_start_event)
