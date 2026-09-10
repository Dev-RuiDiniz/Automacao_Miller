from datetime import date

from infra.dou.collector import build_requests, date_range


def test_date_range_is_inclusive_and_requests_cover_pdf_xml_and_extras() -> None:
    assert date_range(date(2026, 8, 12), date(2026, 8, 12)) == [date(2026, 8, 12)]
    requests = build_requests(date(2026, 8, 12), date(2026, 8, 13))
    assert len(requests) == 18
    assert any(item.kind == "pdf" and item.section == "do1" and "ASSINADO_do1.pdf" in item.filename for item in requests)
    assert any(item.kind == "xml" and item.section == "DO1E" and item.filename.endswith("-DO1E.zip") for item in requests)


def test_urls_are_based_on_official_inlabs_download_shape() -> None:
    request = build_requests(date(2026, 9, 10), date(2026, 9, 10))[0]
    assert request.url.startswith("https://inlabs.in.gov.br/index.php?p=2026-09-10&dl=")
