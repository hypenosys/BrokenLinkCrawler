"""Explicit same-origin scope decisions. No implicit wildcard subdomains."""
from dataclasses import dataclass
from urllib.parse import urlsplit


def url_origin(url):
    parts = urlsplit(url)
    return (parts.scheme, parts.hostname, parts.port or (443 if parts.scheme == "https" else 80))


@dataclass(frozen=True)
class ScopePolicy:
    """Allow only the configured effective origin; redirects need separate approval."""
    root_url: str

    def allows(self, url: str) -> bool:
        return url_origin(url) == url_origin(self.root_url)

    def require(self, url: str) -> None:
        if not self.allows(url):
            raise ValueError("Redirect outside origin blocked")
