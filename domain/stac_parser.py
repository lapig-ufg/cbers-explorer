from .models import StacItem, StacCollection, SearchResult


def parse_item(data):
    return StacItem.from_dict(data)


def parse_collection(data):
    return StacCollection.from_dict(data)


def parse_search_result(data):
    features = data.get("features", [])
    items = [parse_item(f) for f in features]

    context = data.get("context", {})
    matched = context.get("matched", len(items))
    returned = context.get("returned", len(items))

    links = data.get("links", [])
    next_page = extract_next_page(links)
    prev_page = extract_prev_page(links)

    return SearchResult(
        items=items,
        matched=matched,
        returned=returned,
        next_page=next_page,
        prev_page=prev_page,
    )


def parse_collections_response(data):
    collections_raw = data.get("collections", [])
    return [parse_collection(c) for c in collections_raw]


def extract_next_page(links):
    for link in links:
        if link.get("rel") == "next":
            href = link.get("href", "")
            return _extract_page_from_href(href)
    return None


def extract_prev_page(links):
    for link in links:
        if link.get("rel") == "prev" or link.get("rel") == "previous":
            href = link.get("href", "")
            return _extract_page_from_href(href)
    return None


def _extract_page_from_href(href):
    if not href:
        return None
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)
        page_values = qs.get("page", [])
        if page_values:
            return int(page_values[0])
    except (ValueError, IndexError):
        pass
    return None
