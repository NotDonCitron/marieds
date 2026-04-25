import httpx
from scrapers.base import ListingResult

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def notify(self, result: ListingResult):
        if not self.webhook_url: return
        
        embed = {
            "title": f"🎮 {result.title}",
            "url": result.url,
            "color": 0x00ff00,
            "fields": [
                {"name": "Preis", "value": f"{result.price}€", "inline": True},
                {"name": "Plattform", "value": result.platform, "inline": True},
                {"name": "Ort", "value": result.location or "Unbekannt", "inline": True},
            ],
            "footer": {"text": "Nintendo 3DS XL Suche"}
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(self.webhook_url, json={"embeds": [embed]})
