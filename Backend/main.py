from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS from extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to extension origin for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data schema
class URLScanRequest(BaseModel):
    url: str

# Dummy URL scan (replace later with model logic)
@app.post("/scan-url")
async def scan_url(data: URLScanRequest):
    url = data.url
    # dummy logic
    is_phishing = "login" in url or "secure" in url
    return {
        "url": url,
        "phishing": is_phishing,
        "confidence": 0.85 if is_phishing else 0.15,
        "message": "Likely phishing" if is_phishing else "Looks safe"
    }
