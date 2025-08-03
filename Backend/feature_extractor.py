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
    }

    return list(features.values())
