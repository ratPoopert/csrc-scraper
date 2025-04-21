from .scraper import Scraper, BeautifulSoup


class CAVPCertificateScraper(Scraper):

    properties = [
        "Description",
        "Implementation Name",
        "Version",
        "Type",
        "Vendor",
    ]

    def scrape(self):
        self.data = {}
        self.scrape_properties()

    def scrape_properties(self):
        for property in self.properties:
            match property:
                case "Vendor":
                    self.scrape_vendor()
                case _:
                    self.scrape_property(property)

    def scrape_property(self, property: str):
        selector = f'div.col-md-2:-soup-contains("{property}")'
        key_el = self.soup.select_one(selector)
        if key_el is None:
            return
        parent_el = key_el.parent
        val_el = parent_el.select_one('div.col-md-10')
        if val_el is None:
            return
        self.data[property] = val_el.text.strip()

    def scrape_vendor(self):
        container = self.soup.select_one(
            'div.col-md-1:-soup-contains("Vendor")'
        ).parent
        vendor_el, contacts_el = container.select('div.col-md-5')
        name = vendor_el.select_one('a').text.strip()
        website = vendor_el.select_one('a').get('href')
        address_els = vendor_el.select('span.indent')
        address_lines = [el.text.strip() for el in address_els]
        self.data["Vendor"] = {
            "Name": name,
            "Website": website,
            "Address": "\n".join(address_lines)
        }
        self.scrape_vendor_contacts(contacts_el)

    def scrape_vendor_contacts(self, contacts_el: BeautifulSoup):
        contacts = []
        strings = list(contacts_el.stripped_strings)
        span_strings = [span.text.strip()
                        for span in contacts_el.select('span.indent')]
        names = [string for string in strings if string not in span_strings]
        contact = []
        contact.append(strings.pop(0))
        while strings:
            string = strings.pop(0)
            if string in names:
                contacts.append(self.scrape_vendor_contact(contact))
                contact = [string]
            elif len(strings) == 0:
                contact.append(string)
                contacts.append(self.scrape_vendor_contact(contact))
                break
            else:
                contact.append(string)
        self.data["Vendor"]["Contacts"] = contacts

    @staticmethod
    def scrape_vendor_contact(contact: list[str]):
        gen = iter(contact)
        contact = {
            "Name": next(gen),
            "Email": next(gen)
        }
        phone = next(gen, '').lstrip("Phone: ")
        if phone != '':
            contact["Phone"] = phone
        fax = next(gen, '').lstrip("Fax: ")
        if fax != '':
            contact["Fax"] = fax
        return contact
