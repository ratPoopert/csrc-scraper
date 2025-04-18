import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    result = {}
    result["Certificate Number"] = _scrape_certificate_number(soup)

    panels = soup.find_all('div', class_="panel panel-default")
    for panel in panels:
        heading = panel.find('div', class_='panel-heading')
        body = panel.find('div', class_='panel-body')
        key = heading.text.strip()
        data = _scrape_panel(key, body)
        result[key] = data
    return result


def _scrape_certificate_number(soup: BeautifulSoup) -> str:
    return soup.find('h3').text.lstrip("Certificate #").strip()


def _scrape_panel(key: str, soup: BeautifulSoup):
    match key:
        case "Details":
            return _scrape_details_panel(soup)
        case "Vendor":
            return _scrape_vendor_panel(soup)
        case "Related Files":
            return _scrape_related_files_panel(soup)
        case "Validation History":
            return _scrape_validation_history_panel(soup)
        case _:
            return None


def _scrape_details_panel(soup: BeautifulSoup) -> dict:
    result = {}
    rows = soup.find_all('div', class_="row", recursive=False)
    for row in rows:
        label = row.find('div', class_="col-md-3").text.strip()
        content = row.find('div', class_='col-md-9')
        match label:
            case "Overall Level":
                data = int(content.text.strip())
            case "Approved Algorithms":
                data = _scrape_approved_algorithms_table(content)
            case _:
                text = content.text.strip()
                data = re.sub(r'\s+', ' ', text)
        result[label] = data
    return result


def _scrape_approved_algorithms_table(soup: BeautifulSoup):
    tbody = soup.find('tbody')
    rows = tbody.find_all('tr')
    return list(map(_scrape_approved_algorithm_table_row, rows))


def _scrape_approved_algorithm_table_row(soup: BeautifulSoup):
    alg, val = soup.find_all('td', recursive=False)
    return [
        alg.text.strip(),
        val.text.strip(),
        [_resolve_absolute_url(a.get('href')) for a in val.find_all('a')]
    ]


def _scrape_vendor_panel(soup: BeautifulSoup) -> dict:
    return {
        "Name": soup.find('a').text.strip(),
        "Website": soup.find('a').get('href', ''),
        "Address": "\n".join(map(lambda el: el.text.strip(),
                                 soup.find_all('span', recursive=False))),
        "Contacts": _scrape_vendor_contacts(soup.find('div'))
    }


def _scrape_vendor_contacts(soup: BeautifulSoup) -> list[dict]:
    return list(map(_scrape_vendor_contact,
                    soup.find_all('span', recursive=False)))


def _scrape_vendor_contact(soup: BeautifulSoup) -> dict:
    strings = soup.stripped_strings
    result = {
        "Name": next(strings),
        "Email": next(strings)
    }

    phone_str = next(strings, '')
    phone = phone_str.lstrip("Phone: ") if "Phone: " in phone_str else None
    fax_str = next(strings, '')
    fax = fax_str.lstrip("Fax: ") if "Fax: " in fax_str else None

    if phone:
        result["Phone"] = phone
    if fax:
        result["Fax"] = fax
    return result


def _scrape_related_files_panel(soup: BeautifulSoup) -> list:
    return [[el.text.strip(), _resolve_absolute_url(el.get('href'))]
            for el in soup.find_all('a')]


def _scrape_validation_history_panel(soup: BeautifulSoup) -> list[dict]:
    return list(map(_scrape_validation_history_table_row,
                    soup.find('tbody').find_all('tr')))


def _scrape_validation_history_table_row(soup: BeautifulSoup) -> dict:
    cells = soup.find_all('td')
    return {
        "Date": cells[0].text.strip(),
        "Type": cells[1].text.strip(),
        "Lab": cells[2].text.strip(),
    }


def _resolve_absolute_url(relative_url: str) -> str:
    base_url = "https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/"
    return urljoin(base_url, relative_url)
