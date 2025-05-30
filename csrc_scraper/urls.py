import urllib.parse

CSRC_BASE_URL = "https://csrc.nist.gov/"

CAVP_BASE_URL = CSRC_BASE_URL + \
    "projects/Cryptographic-Algorithm-Validation-Program/"

CAVP_CERTIFICATE_BASE_URL = CAVP_BASE_URL + "details"

CMVP_BASE_URL = CSRC_BASE_URL + \
    "projects/cryptographic-module-validation-program/"

CMVP_CERTIFICATE_BASE_URL = CMVP_BASE_URL + "certificate/"


def join(base_url, relative_url):
    return urllib.parse.urljoin(
        base_url,
        encode(relative_url)
    )


def encode(url: str) -> str:
    return urllib.parse.quote(url, "/:?&=")
