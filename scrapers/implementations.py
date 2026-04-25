from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from scrapers.base import BaseScraper, ListingResult

class EbayScraper(BaseScraper):
    platform_name = "eBay"
    base_url = "https://www.ebay.de"

    async def scrape(self, query: str) -> list[ListingResult]:
        client = await self._get_client()
        params = {
            "_nkw": query,
            "_sacat": "139971",
            "LH_ItemCondition": "3000|7000",
            "_sop": "15",
            "_ipg": "60"
        }
        resp = await client.get(f"{self.base_url}/sch/i.html", params=params)
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        items = soup.select("li.s-item, .s-item__wrapper")
        for item in items:
            title_el = item.select_one(".s-item__title span[role='heading'], .s-item__title")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            if "Shop on eBay" in title: continue
            
            price_el = item.select_one(".s-item__price")
            price, price_text = self.extract_price(price_el.get_text() if price_el else None)
            
            link_el = item.select_one(".s-item__link")
            if not link_el: continue
            url = link_el["href"].split("?")[0]
            
            results.append(ListingResult(title=title, url=url, platform=self.platform_name, price=price, price_text=price_text))
        return results

class KleinanzeigenScraper(BaseScraper):
    platform_name = "Kleinanzeigen"
    base_url = "https://www.kleinanzeigen.de"

    async def scrape(self, query: str) -> list[ListingResult]:
        # Sauberes URL-Encoding für Kleinanzeigen
        encoded_query = quote_plus(query).replace("+", "-")
        url = f"{self.base_url}/s-{encoded_query}/k0"
        html = await self._stealth_get(url)
        soup = BeautifulSoup(html, "lxml")
        results = []
        for item in soup.select("article.aditem"):
            title_el = item.select_one(".aditem-main h2 a")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            
            price_el = item.select_one(".aditem-main--middle--price-shipping--price")
            price, price_text = self.extract_price(price_el.get_text() if price_el else None)
            
            url = f"{self.base_url}{title_el['href']}" if title_el.get("href") else ""
            location_el = item.select_one(".aditem-main--top--left")
            location = location_el.get_text(strip=True) if location_el else None
            
            results.append(ListingResult(title=title, url=url, platform=self.platform_name, price=price, price_text=price_text, location=location))
        return results

class AllegroScraper(BaseScraper):
    platform_name = "Allegro.pl"
    base_url = "https://allegro.pl"

    async def scrape(self, query: str) -> list[ListingResult]:
        pl_queries = {
            "Nintendo 3DS XL schwarz": "Nintendo 3DS XL czarna",
            "3DS XL schwarz": "3DS XL czarny",
            "Nintendo 3DS XL black": "Nintendo 3DS XL czarna konsola"
        }
        search_query = pl_queries.get(query, query)
        url = f"{self.base_url}/listing?string={quote_plus(search_query)}"
        try:
            html = await self._stealth_get(url, wait_ms=5000)
        except Exception:
            url = f"{self.base_url}/listing?string=3DS%20XL%20konsola"
            html = await self._stealth_get(url, wait_ms=5000)

        soup = BeautifulSoup(html, "lxml")
        results = []
        items = soup.select("[data-testid='listing-item'], article")
        for item in items:
            try:
                title_el = item.select_one("h2 a, [data-testid='listing-item-title']")
                if not title_el: continue
                title = title_el.get_text(strip=True)
                if not any(kw in title.lower() for kw in ["czarn", "black", "schwarz"]):
                    continue
                price_el = item.select_one("[data-testid='listing-item-price']")
                price, price_text = self.extract_price(price_el.get_text() if price_el else None)
                if price and "zł" in (price_text or "").lower():
                    price = round(price / 4.3, 2)
                    price_text = f"~{price}€ ({price_text})"
                url = title_el["href"] if title_el.get("href") else ""
                if url.startswith("/"): url = f"{self.base_url}{url}"
                results.append(ListingResult(title=title, url=url, platform=self.platform_name, price=price, price_text=price_text, location="Polen"))
            except: continue
        return results

class VintedScraper(BaseScraper):
    platform_name = "Vinted"
    base_url = "https://www.vinted.de"

    async def scrape(self, query: str) -> list[ListingResult]:
        url = f"{self.base_url}/catalog?search_text={quote_plus(query)}"
        html = await self._stealth_get(url, wait_ms=5000)
        soup = BeautifulSoup(html, "lxml")
        results = []
        items = soup.select("[data-testid^='product-item']")
        for item in items:
            try:
                title_el = item.select_one(".feed-grid__item-title, [class*='title'], h2")
                title = title_el.get_text(strip=True) if title_el else "Nintendo 3DS XL"
                price_el = item.select_one("[data-testid$='-price']")
                price, price_text = self.extract_price(price_el.get_text() if price_el else None)
                link_el = item.select_one("a[href*='/items/']")
                url = f"{self.base_url}{link_el['href']}" if link_el else ""
                results.append(ListingResult(title=title, url=url, platform=self.platform_name, price=price, price_text=price_text))
            except: continue
        return results
