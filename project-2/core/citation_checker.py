from .document_loader import normalize

def verify(citation, pages):
    name, page = citation.relative_path, citation.page
    # The exact manifest key is the canonical top-level POSIX path.
    if name not in pages:
        return None, "unknown_or_unsafe_path"
    if not 1 <= page <= len(pages[name]):
        return None, "page_out_of_bounds"
    q = normalize(citation.quote)
    if len(q.split()) < 3 or len(q) < 12:
        return None, "quote_too_short"
    if f" {q} " not in f" {normalize(pages[name][page-1])} ":
        return None, "unverified_quote"
    return (name, page, q), None

def supports(anchor, verified):
    path, page, phrase = anchor
    q = normalize(phrase)
    return any((n, p) == (path, page) and f" {q} " in f" {quote} " for n,p,quote in verified)

