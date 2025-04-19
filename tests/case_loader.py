import json
from pathlib import Path


def cmvp_certificate_cases() -> tuple[tuple]:
    base_dir = Path(__file__).parent
    return load_cases(base_dir/'examples/cmvp/certificates')


def load_cases(base_dir: Path) -> tuple[tuple]:
    html_dir = base_dir/'html'
    json_dir = base_dir/'json'
    for d in [base_dir, html_dir, json_dir]:
        assert d.exists() and d.is_dir()
    html_files = sorted(list(html_dir.glob("*.html")))
    json_files = sorted(list(filter(lambda f: "schema" not in str(f),
                        json_dir.glob("*.json"))))
    assert len(html_files) == len(json_files)
    html_strs = map(lambda f: f.read_text(), html_files)
    json_strs = map(lambda f: f.read_text(), json_files)
    data = map(json.loads, json_strs)
    cases = tuple(zip(html_strs, data))
    return cases
