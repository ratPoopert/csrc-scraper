from .case_loader import cmvp_certificate_cases
from csrc_scraper.scraper import get_scraper
from csrc_scraper import urls


def get_result(case) -> dict:
    html = case[0]
    url = urls.CMVP_CERTIFICATE_BASE_URL
    scraper = get_scraper(url, html)
    scraper.scrape()
    return scraper.data


CASES = cmvp_certificate_cases()
RESULTS = list(map(get_result, CASES))


def test_scrapes_certificate_number():
    for i in range(len(CASES)):
        data = CASES[i][1]
        expected = data.get("Certificate Number")
        actual = RESULTS[i].get("Certificate Number")
        msg = f"Certificate {data['Certificate Number']}, Certificate Number"
        assert expected == actual, msg


def test_scrapes_details_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        expected = data.get("Details")
        actual = RESULTS[i].get("Details")
        for key in expected:
            msg = f"Certificate {data['Certificate Number']}, Details, {key}"
            assert expected[key] == actual[key], msg


def test_scrapes_vendor_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        expected = data.get("Vendor")
        actual = RESULTS[i].get("Vendor")
        for key in expected:
            msg = f"Certificate {data['Certificate Number']}, Vendor, {key}"
            assert expected[key] == actual[key], msg


def test_scrapes_related_files_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        expected = data.get("Related Files")
        actual = RESULTS[i].get("Related Files")
        msg = f"Certificate {data['Certificate Number']}, Related Files"
        assert expected == actual, msg


def test_scrapes_validation_history_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        expected = data.get("Validation History")
        actual = RESULTS[i].get("Validation History")
        msg = f"Certificate {data['Certificate Number']}, Validation History"
        assert expected == actual, msg
