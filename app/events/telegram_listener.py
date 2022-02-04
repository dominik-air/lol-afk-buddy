from external_messaging.telegram import post_telegram_message
from .event import subscribe


def handle_game_found_event(account: str):
    post_telegram_message(account=account, msg="[LoL AFK Buddy] Game Found! You are now in champion select.")


def handle_champion_ban_event(account: str):
    post_telegram_message(account=account, msg="[LoL AFK Buddy] Champion Banned! You are now in picking phase.")


def handle_champion_pick_event(account: str):
    post_telegram_message(account=account, msg="[LoL AFK Buddy] Champion Picked! You are now in loadout phase.")


def handle_game_start_event(account: str):
    post_telegram_message(account=account, msg="[LoL AFK Buddy] The game has begun! You are now in game.")


def setup_telegram_event_handlers():
    """Subscribe telegram events to event types here."""
    subscribe("game_found", handle_game_found_event)
    subscribe("champion_ban", handle_champion_ban_event)
    subscribe("champion_pick", handle_champion_pick_event)
    subscribe("game_start", handle_game_start_event)
