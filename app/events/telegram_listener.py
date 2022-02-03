from external_messaging.telegram import post_telegram_message
from .event import subscribe


def handle_game_found_event(account: str):
    post_telegram_message(account=account, msg="[LoL AFK Buddy] Game Found! You are now in champion select.")

# TODO: possible events: pick, bans, game start


def setup_telegram_event_handlers():
    subscribe("game_found", handle_game_found_event)
