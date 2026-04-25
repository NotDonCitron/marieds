import os
import asyncio
from dotenv import load_dotenv
from scrapers.implementations import EbayScraper, KleinanzeigenScraper, AllegroScraper, VintedScraper
from notifier import DiscordNotifier
from filters import is_good_listing, listing_score
from storage import init_db, has_seen, save_seen
from rich.console import Console
from rich.table import Table

load_dotenv()

async def main():
    console = Console()
    init_db()
    queries = ["Nintendo 3DS XL schwarz", "3DS XL schwarz", "Nintendo 3DS XL black"]
    max_price = 120.0
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    notifier = DiscordNotifier(webhook_url) if webhook_url else None
    
    console.print(f"[bold blue]Suche nach:[/bold blue] {queries} (Max Ziel: {max_price}€)")
    
    scrapers = [EbayScraper(), KleinanzeigenScraper(), AllegroScraper(), VintedScraper()]
    all_results = []
    
    for scraper in scrapers:
        for query in queries:
            try:
                console.print(f"[yellow]Scraping {scraper.platform_name} für '{query}'...[/yellow]")
                results = await scraper.scrape(query)
                all_results.extend(results)
            except Exception as e:
                console.print(f"[red]Fehler bei {scraper.platform_name} ('{query}'): {e}[/red]")
        await scraper.close()

    # Deduplizierung nach URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            unique_results.append(r)
    all_results = unique_results

    # Filtern
    console.print(f"[cyan]Gefunden insgesamt (vor Filtern): {len(all_results)}[/cyan]")
    
    filtered = []
    for r in all_results:
        if is_good_listing(r, max_visible_price=160.0):
            filtered.append(r)
    
    # Sortieren nach Preis und Score
    filtered.sort(key=lambda x: (x.price if x.price else 999, -listing_score(x)))

    table = Table(title=f"Ergebnisse für Nintendo 3DS XL (Max Ziel: {max_price}€)")
    table.add_column("Plattform", style="cyan")
    table.add_column("Titel", style="white")
    table.add_column("Preis", style="green", justify="right")
    table.add_column("Ort", style="magenta")
    table.add_column("Link", style="blue")

    for r in filtered:
        is_new = not has_seen(r)
        price_style = "bold green" if r.price <= max_price else "yellow"
        
        # In die Tabelle aufnehmen
        table.add_row(
            f"{'[bold yellow]NEW[/bold yellow] ' if is_new else ''}{r.platform}",
            r.title[:50], 
            f"[{price_style}]{r.price}€[/{price_style}]", 
            r.location or "-", 
            r.url
        )
        
        # Discord-Benachrichtigung nur für NEUE Angebote im Budget
        if notifier and r.price <= max_price and is_new:
            await notifier.notify(r)
        
        # In Datenbank speichern
        save_seen(r)

    console.print(table)
    console.print(f"\n[bold green]Gefunden:[/bold green] {len(filtered)} passende Angebote.")

if __name__ == "__main__":
    asyncio.run(main())
