# 🎮 MarieDS - Nintendo 3DS XL Scraper

Ein automatisierter Scraper, der verschiedene europäische Marktplätze nach einem **Nintendo 3DS XL** (Fokus: Schwarz) durchsucht.

## ✨ Features

- **Multi-Plattform Suche**: eBay.de, Kleinanzeigen.de, Vinted.de und Allegro.pl.
- **Intelligente Filter**: Automatische Filterung von Spielen, Zubehör und defekten Geräten.
- **Preis-Check**: Sucht gezielt nach Angeboten im gewünschten Budget (Ziel: < 120€).
- **Internationaler Vergleich**: Durchsucht Allegro.pl mit automatischen polnischen Suchbegriffen und Währungsumrechnung (PLN -> EUR).
- **Discord Integration**: Sendet sofortige Benachrichtigungen über gefundene Schnäppchen via Webhook.
- **Stealth Mode**: Nutzt Playwright-Stealth, um Bot-Erkennung auf Plattformen wie Kleinanzeigen oder Vinted zu minimieren.

## 🚀 Installation

1. Repo klonen:
   ```bash
   git clone https://github.com/NotDonCitron/marieds.git
   cd marieds
   ```

2. Virtuelle Umgebung erstellen und Dependencies installieren:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Konfiguration:
   Erstelle eine `.env` Datei im Hauptverzeichnis:
   ```env
   DISCORD_WEBHOOK_URL=dein_discord_webhook_link
   ```

## 🛠 Nutzung

Einfach den Scraper starten:
```bash
python main.py
```

## ⚙️ Architektur

- **Python 3.10+**
- **Playwright**: Für JavaScript-lastige Seiten und Bot-Protection.
- **BeautifulSoup4**: Für effizientes HTML-Parsing.
- **Asyncio / HTTPX**: Für parallele Abfragen und hohe Geschwindigkeit.
- **Rich**: Für eine schicke Terminal-Ausgabe.

## 📄 Lizenz

MIT
