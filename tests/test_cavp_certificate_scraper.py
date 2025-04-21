from csrc_scraper import urls
from csrc_scraper.scraper import get_scraper
from csrc_scraper.cavp_certificate_scraper import CAVPCertificateScraper
from .case_loader import cavp_certificate_cases


def get_result(case) -> dict:
    html = case[0]
    url = urls.CAVP_CERTIFICATE_BASE_URL
    scraper = get_scraper(url, html)
    scraper.scrape()
    return scraper.data


CASES = cavp_certificate_cases()
RESULTS = list(map(get_result, CASES))


def test_scrapes_properties():
    for i in range(len(CASES)):
        data = CASES[i][1]
        for prop in CAVPCertificateScraper.properties:
            expected = data.get(prop)
            actual = RESULTS[i].get(prop)
            assert expected == actual
