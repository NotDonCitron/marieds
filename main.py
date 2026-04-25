import os
import asyncio
from dotenv import load_dotenv
from scrapers.implementations import EbayScraper, KleinanzeigenScraper, AllegroScraper, VintedScraper
from notifier import DiscordNotifier
from rich.console import Console
from rich.table import Table

load_dotenv()

async def main():
    console = Console()
    queries = ["Nintendo 3DS XL schwarz", "3DS XL schwarz", "Nintendo 3DS XL black"]
    max_price = 120.0
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    notifier = DiscordNotifier(webhook_url) if webhook_url else None
    
    console.print(f"[bold blue]Suche nach:[/bold blue] {queries} (Max: {max_price}€)")
    
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
        if not r.price:
            continue
            
        # Wir zeigen alles bis 160€ an, damit man sieht was es gibt, 
        # aber wir markieren später was im Budget (120€) ist.
        if r.price > 160: 
            continue
        
        title_lower = r.title.lower()
        
        # Muss 3DS XL sein
        if not ("3ds" in title_lower and "xl" in title_lower):
            continue
            
        # Farbe - Wir sind jetzt SEHR tolerant
        # Wir schließen nur aus, wenn EXKLUSIV eine falsche Farbe genannt wird
        # Wenn gar keine Farbe genannt wird, lassen wir es zu
        wrong_colors = ["pink", "weiß", "white", "rot", "red", "blau", "blue", "türkis", "silver", "silber"]
        is_specifically_wrong = any(c in title_lower for c in wrong_colors) and not any(c in title_lower for c in ["schwarz", "black", "czarn"])
        
        if is_specifically_wrong:
            continue

        # Ausschluss von reinen Kartons oder nur Ladekabeln
        if any(kw in title_lower for kw in ["nur karton", "ovp ohne konsole", "leerkarton", "box only"]):
            continue
            
        # Wenn im Titel "defekt", "kaputt" oder "parts" steht -> raus
        if any(kw in title_lower for kw in ["defekt", "kaputt", "schaden", "broken", "uszkodzon"]):
            continue

        filtered.append(r)
    
    # Sortieren nach Preis
    filtered.sort(key=lambda x: x.price if x.price else 999)

    table = Table(title=f"Ergebnisse für Nintendo 3DS XL (Max Ziel: {max_price}€)")
    table.add_column("Plattform", style="cyan")
    table.add_column("Titel", style="white")
    table.add_column("Preis", style="green", justify="right")
    table.add_column("Ort", style="magenta")
    table.add_column("Link", style="blue")

    for r in filtered:
        # Budget-Check für Farbe in der Tabelle
        price_style = "bold green" if r.price <= max_price else "yellow"
        table.add_row(
            r.platform, 
            r.title[:50], 
            f"[{price_style}]{r.price}€[/{price_style}]", 
            r.location or "-", 
            r.url
        )
        if notifier and r.price <= max_price:
            await notifier.notify(r)

    console.print(table)
    console.print(f"\n[bold green]Gefunden:[/bold green] {len(filtered)} passende Angebote.")

if __name__ == "__main__":
    asyncio.run(main())
