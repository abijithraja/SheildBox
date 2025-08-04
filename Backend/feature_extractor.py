# feature_extractor.py
import re
from urllib.parse import urlparse
import tldextract

def extract_features(url):
    parsed = urlparse(url)
    ext = tldextract.extract(url)

    features = {
        "url_length": len(url),
        "has_ip": bool(re.search(r'\d+\.\d+\.\d+\.\d+', parsed.netloc)),
        "has_https": parsed.scheme == "https",
        "num_dots": url.count('.'),
        "num_hyphens": url.count('-'),
        "num_digits": sum(c.isdigit() for c in url),
        "has_at_symbol": "@" in url,
        "has_suspicious_words": any(w in url.lower() for w in ["login", "verify", "secure", "bank", "phish"]),
        # Advanced features:
        "subdomain_length": len(ext.subdomain),
        "path_length": len(parsed.path),
        "query_length": len(parsed.query),
        "num_parameters": parsed.query.count('&') + 1 if parsed.query else 0,
        "has_double_slash_redirect": "//" in url[url.find("//")+2:],  # check after first '//' in protocol
        "starts_with_http": url.startswith("http://")
    }

    return list(features.values())
