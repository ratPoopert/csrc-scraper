from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from .urls import (
    CMVP_CERTIFICATE_BASE_URL,
    CAVP_CERTIFICATE_BASE_URL
)


class Scraper(ABC):
    """
    A customized HTML scraper.
    """

    def __init__(self, html: str):
        if not isinstance(html, str):
            raise TypeError("HTML must be a string.")
        self.soup = BeautifulSoup(html, 'html.parser')
        self.data = None

    @abstractmethod
    def scrape(self):
        """
        Populates the scraper's data property with data scraped from
        the scraper's HTML.
        """
        pass


def get_scraper(url: str, html: str) -> Scraper:
    """
    Returns the appropriate scraper based on the URL prefix.
    Raises error if no scraper is found for the given URL.
    """
    if url.startswith(CMVP_CERTIFICATE_BASE_URL):
        from .cmvp_certificate_scraper import CMVPCertificateScraper
        return CMVPCertificateScraper(html)
    if url.startswith(CAVP_CERTIFICATE_BASE_URL):
        from .cavp_certificate_scraper import CAVPCertificateScraper
        return CAVPCertificateScraper(html)
    raise NotImplementedError(f"No scraper implemented for URL {url}")
