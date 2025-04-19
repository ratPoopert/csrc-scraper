from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class Scraper(ABC):

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.data = None

    @abstractmethod
    def scrape(self):
        pass
