import re
from scrapers.base import ListingResult

REQUIRED_PATTERNS = [
    r"\b3ds\s*xl\b",
    r"\bnintendo\s*3ds\s*xl\b",
    r"\bnew\s*3ds\s*xl\b",
]

CONSOLE_WORDS = [
    "konsole", "console", "handheld", "system", "gerät", "geraet",
    "nintendo 3ds xl", "3ds xl",
]

BLACK_WORDS = [
    "schwarz", "black", "czarn", "czarna", "nero", "negro", "preto", "noir",
]

WRONG_COLORS = [
    "pink", "weiß", "weiss", "white", "rot", "red", "blau", "blue",
    "türkis", "turkis", "silver", "silber", "rosa",
]

HARD_REJECT_WORDS = [
    "defekt", "kaputt", "broken", "for parts", "parts only", "ersatzteil",
    "spares", "uszkodzon", "beschädigt", "display", "touchscreen", "gehäuse",
    "shell", "housing", "akku", "battery", "ladekabel", "ladegerät", "netzteil",
    "stylus", "stift", "tasche", "case", "hülle", "schutzfolie", "screen protector",
    "kartenleser", "sd karte", "sd card", "leerkarton", "nur karton", "box only",
    "ovp ohne konsole",
]

GAME_WORDS = [
    "spiel", "spiele", "game", "games", "cartridge", "modul", "pokemon",
    "mario kart", "zelda", "animal crossing", "luigi", "yokai",
    "professor layton",
]

def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def looks_like_3ds_xl(title: str) -> bool:
    title = normalize_text(title)
    if "2ds" in title: return False
    return any(re.search(pattern, title) for pattern in REQUIRED_PATTERNS)

def is_wrong_color(title: str) -> bool:
    title = normalize_text(title)
    has_black = any(word in title for word in BLACK_WORDS)
    has_wrong_color = any(word in title for word in WRONG_COLORS)
    return has_wrong_color and not has_black

def is_probably_accessory_or_game(title: str, price: float | None) -> bool:
    title = normalize_text(title)
    has_console_word = any(word in title for word in CONSOLE_WORDS)
    has_game_word = any(word in title for word in GAME_WORDS)
    has_hard_reject = any(word in title for word in HARD_REJECT_WORDS)
    if has_hard_reject: return True
    if price is not None and price < 45: return True
    if has_game_word and not has_console_word: return True
    return False

def listing_score(result: ListingResult) -> int:
    title = normalize_text(result.title)
    score = 0
    if "nintendo" in title: score += 2
    if "3ds" in title: score += 3
    if "xl" in title: score += 3
    if "new 3ds xl" in title: score += 2
    if any(word in title for word in CONSOLE_WORDS): score += 3
    if any(word in title for word in BLACK_WORDS): score += 2
    if result.price and 70 <= result.price <= 140: score += 2
    if any(word in title for word in GAME_WORDS): score -= 2
    if any(word in title for word in HARD_REJECT_WORDS): score -= 10
    if is_wrong_color(title): score -= 5
    return score

def is_good_listing(result: ListingResult, max_visible_price: float = 160.0) -> bool:
    if not result.price: return False
    if result.price > max_visible_price: return False
    if not looks_like_3ds_xl(result.title): return False
    if is_wrong_color(result.title): return False
    if is_probably_accessory_or_game(result.title, result.price): return False
    return listing_score(result) >= 5
