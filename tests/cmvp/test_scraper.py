from .case_loader import load_cases
from csrc_scraper import cmvp

CASES = load_cases()[0:1]
RESULTS = list(map(lambda case: cmvp.scrape(case[0]), CASES))


def test_scrapes_certificate_number():
    for i in range(len(CASES)):
        data = CASES[i][1]
        expected = data.get("Certificate Number")
        actual = RESULTS[i].get("Certificate Number")
        assert expected == actual


def test_scrapes_details_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        print(data["Certificate Number"])
        expected = data.get("Details")
        actual = RESULTS[i].get("Details")
        for key in expected:
            assert expected[key] == actual[key]


def test_scrapes_vendor_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        print(data["Certificate Number"])
        expected = data.get("Vendor")
        actual = RESULTS[i].get("Vendor")
        for key in expected:
            assert expected[key] == actual[key]


def test_scrapes_related_files_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        print(data["Certificate Number"])
        expected = data.get("Related Files")
        actual = RESULTS[i].get("Related Files")
        assert expected == actual


def test_scrapes_validation_history_panel():
    for i in range(len(CASES)):
        data = CASES[i][1]
        print(data["Certificate Number"])
        expected = data.get("Validation History")
        actual = RESULTS[i].get("Validation History")
        assert expected == actual
