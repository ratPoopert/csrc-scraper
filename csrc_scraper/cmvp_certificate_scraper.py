from .scraper import Scraper, BeautifulSoup

from . import helpers, urls


class CMVPCertificateScraper(Scraper):

    def scrape(self):
        self.data = {}
        self.scrape_certificate_number()
        self.scrape_panels()

    def scrape_certificate_number(self):
        heading_text = self.soup.find('h3').text
        certificate_number = heading_text.lstrip("Certificate #").strip()
        self.data["Certificate Number"] = certificate_number

    def scrape_panels(self):
        panels = map(
            Panel,
            self.soup.find_all('div', class_="panel panel-default")
        )
        for panel in panels:
            panel.scrape()
            self.data[panel.heading] = panel.data


class Panel:

    def __init__(self, soup: BeautifulSoup):
        self.heading = soup.find('div', class_='panel-heading').text.strip()
        self.body = soup.find('div', class_='panel-body')
        self.data = self.data_type()

    @property
    def heading(self):
        pass

    @property
    def data_type(self):
        pass

    def scrape(self):
        pass

    def __new__(cls, soup: BeautifulSoup):
        if cls is Panel:
            heading = soup.find('div', class_='panel-heading').text.strip()
            panels = [
                DetailsPanel,
                VendorPanel,
                RelatedFilesPanel,
                ValidationHistoryPanel
            ]
            for panel in panels:
                if heading == panel.heading:
                    return super().__new__(panel)
            raise NotImplementedError(f"Unrecognized panel: {heading}")
        super().__new__(cls, soup)


class DetailsPanel(Panel):
    heading = "Details"
    data_type = dict

    def scrape(self):
        rows = self.body.find_all('div', class_="row", recursive=False)
        for row in rows:
            self.scrape_row(row)

    def scrape_row(self, row: BeautifulSoup) -> tuple:
        label = row.find('div', class_="col-md-3").text.strip()
        content = row.find('div', class_='col-md-9')
        match label:
            case "Overall Level":
                data = int(content.text.strip())
            case "Approved Algorithms":
                data = _scrape_approved_algorithms_table(content)
            case ("Security Level Exceptions" |
                  "Tested Configuration(s)"):
                data = list(map(helpers.remove_newlines,
                                content.stripped_strings))
            case _:
                data = helpers.condense_inner_whitespace(content.text)
        self.data[label] = data

    def scrape_approved_algorithms(self, content: BeautifulSoup):
        try:
            tbody = content.find('tbody')
            rows = tbody.find_all('tr')
            entries = map(_scrape_approved_algorithm_table_row, rows)
            return list(filter(lambda e: e[0], entries))
        except AttributeError:
            rows = content.find_all('div', class_="row", recursive=False)
            entries = map(_scrape_approved_algorithm_div_row, rows)
            return list(filter(lambda e: e[0], entries))


class VendorPanel(Panel):
    heading = "Vendor"
    data_type = dict

    def scrape(self):
        self.scrape_name()
        self.scrape_website()
        self.scrape_address()
        self.scrape_contacts()

    def scrape_name(self):
        try:
            name = self.body.find('a').text.strip()
        except Exception:
            name = next(self.body.stripped_strings)
        self.data["Name"] = name

    def scrape_address(self):
        lines = self.body.find_all('span', recursive=False)
        cleaned_lines = map(lambda line: line.text.strip(), lines)
        self.data["Address"] = "\n".join(cleaned_lines)

    def scrape_website(self):
        try:
            website = self.body.find('a').get('href', '')
        except Exception:
            website = ""
        self.data["Website"] = website

    def scrape_contacts(self):
        self.data["Contacts"] = _scrape_vendor_contacts(self.body.find('div'))


class RelatedFilesPanel(Panel):
    heading = "Related Files"
    data_type = list

    def scrape(self):
        links = self.body.find_all('a')
        def label(link): return link.text.strip()
        def url(link): return _resolve_absolute_url(link.get('href'))
        self.data = [[label(link), url(link)] for link in links]


class ValidationHistoryPanel(Panel):
    heading = "Validation History"
    data_type = list

    def scrape(self):
        rows = self.body.find('tbody').find_all('tr')
        for row in rows:
            self.scrape_row(row)

    def scrape_row(self, row: BeautifulSoup):
        cells = row.find_all('td')
        self.data.append({
            "Date": cells[0].text.strip(),
            "Type": cells[1].text.strip(),
            "Lab": cells[2].text.strip(),
        })


def _scrape_approved_algorithms_table(soup: BeautifulSoup):
    try:
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        entries = map(_scrape_approved_algorithm_table_row, rows)
        return list(filter(lambda e: e[0], entries))
    except AttributeError:
        rows = soup.find_all('div', class_="row", recursive=False)
        entries = map(_scrape_approved_algorithm_div_row, rows)
        return list(filter(lambda e: e[0], entries))


def _scrape_approved_algorithm_table_row(soup: BeautifulSoup):
    alg, val = soup.find_all('td', recursive=False)
    return [
        alg.text.strip(),
        val.text.strip(),
        [_resolve_absolute_url(a.get('href')) for a in val.find_all('a')]
    ]


def _scrape_approved_algorithm_div_row(soup: BeautifulSoup):
    alg = soup.find('div', class_="col-md-3")
    val = soup.find('div', class_="col-md-4")
    return [
        alg.text.strip(),
        val.text.strip(),
        [_resolve_absolute_url(a.get('href')) for a in val.find_all('a')]
    ]


def _scrape_vendor_panel(soup: BeautifulSoup) -> dict:
    try:
        name = soup.find('a').text.strip()
        website = soup.find('a').get('href', '')
    except AttributeError:
        name = next(soup.stripped_strings)
        website = ""
    return {
        "Name": name,
        "Website": website,
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
    return urls.join(urls.CMVP_CERTIFICATE_BASE_URL, relative_url)
