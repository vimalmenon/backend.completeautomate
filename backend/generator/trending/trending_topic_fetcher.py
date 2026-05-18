"""Fetches trending topics from Google Trends and Google News."""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

import requests
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

TRENDING_CACHE_MINUTES = 15
GOOGLE_NEWS_TECH_URL = (
    "https://news.google.com/rss/topics/"
    "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB"
    "?hl=en-US&gl=US&ceid=US:en"
)
GOOGLE_NEWS_TOP_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"


@dataclass
class TrendingSource:
    """A single piece of trending data from any source."""

    title: str
    source: str  # 'google_trends', 'google_news', etc.
    score: float | None = None  # Normalized relevance score (0-100)
    url: str | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TrendingTopicFetcher:
    """Aggregate trending topics from multiple free sources."""

    def __init__(self) -> None:
        self._pytrends: TrendReq | None = None

    @property
    def pytrends(self) -> TrendReq:
        if self._pytrends is None:
            self._pytrends = TrendReq(hl="en-US", tz=360)
        return self._pytrends

    def fetch_all(self, niche: str = "") -> list[TrendingSource]:
        """Fetch trending from all available sources."""
        results: list[TrendingSource] = []
        results.extend(self._fetch_google_news())
        results.extend(self._fetch_google_trends(niche))
        results.extend(self._fetch_trending_suggestions(niche))
        return results

    def _fetch_google_news(self) -> list[TrendingSource]:
        """Fetch top stories from Google News RSS."""
        results: list[TrendingSource] = []
        try:
            r = requests.get(GOOGLE_NEWS_TOP_URL, timeout=15)
            r.raise_for_status()
            from xml.etree import ElementTree

            root = ElementTree.fromstring(r.content)
            for item in root.findall(".//item"):
                title_el = item.find("title")
                link_el = item.find("link")
                if title_el is not None and title_el.text:
                    title_text = title_el.text.strip()
                    link = (
                        link_el.text.strip()
                        if link_el is not None and link_el.text
                        else None
                    )
                    results.append(
                        TrendingSource(
                            title=title_text,
                            source="google_news",
                            url=link,
                        )
                    )
        except Exception:
            logger.exception("Failed to fetch Google News RSS")
        return results

    def _fetch_google_trends(self, niche: str) -> list[TrendingSource]:
        """Fetch search interest trends for the given niche."""
        results: list[TrendingSource] = []
        kw = niche if niche else "AI technology"
        try:
            self.pytrends.build_payload(kw_list=[kw], timeframe="now 7-d", geo="US")
            df = self.pytrends.interest_over_time()
            if df is not None and not df.empty and kw in df.columns:
                avg = df[kw].mean()
                results.append(
                    TrendingSource(
                        title=f"Search interest for '{kw}': {avg:.0f}/100 (7-day avg)",
                        source="google_trends",
                        score=float(avg),
                    )
                )
        except Exception:
            logger.exception("Failed to fetch Google Trends interest")
        return results

    def _fetch_trending_suggestions(self, niche: str) -> list[TrendingSource]:
        """Fetch related/rising search suggestions for the niche."""
        results: list[TrendingSource] = []
        if not niche:
            return results
        try:
            suggestions = self.pytrends.suggestions(niche)
            for s in suggestions[:10]:
                title = s.get("title", "")
                if title:
                    results.append(
                        TrendingSource(
                            title=title,
                            source="google_trends_suggestions",
                            url=s.get("mid"),
                        )
                    )
        except Exception:
            logger.exception("Failed to fetch Google Trends suggestions")
        return results

    @staticmethod
    def deduplicate(
        sources: list[TrendingSource], max_items: int = 30
    ) -> list[TrendingSource]:
        """Remove near-duplicates by title (case-insensitive, short titles)."""
        seen: set[str] = set()
        deduped: list[TrendingSource] = []
        for s in sources:
            key = s.title.lower().strip()[:60]
            if key not in seen:
                seen.add(key)
                deduped.append(s)
        return deduped[:max_items]
