import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import smtplib
from email.message import EmailMessage
import os

KEYWORDS = ["mern", "mern stack", "backend", "software engineer", "software developer", "junior", "entry"]
STARTUP_TAGS = ["yc", "y combinator", "series a", "series b", "seed", "startup"]

OUT_CSV = "job_hits.csv"

def fetch_wellfound():
    url = "https://wellfound.com/jobs"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []

    for job in soup.select("a[data-test='JobListing']")[:25]:
        title = job.get_text(strip=True)
        link = "https://wellfound.com" + job["href"]
        jobs.append({
            "site": "Wellfound",
            "title": title,
            "company": "Startup",
            "link": link,
            "time": "Recent"
        })
    return jobs

def filter_jobs(jobs):
    filtered = []
    for j in jobs:
        text = j["title"].lower()
        if any(k in text for k in KEYWORDS):
            if any(s in text for s in STARTUP_TAGS) or "startup" in text:
                filtered.append(j)
    return filtered

jobs = fetch_wellfound()
filtered = filter_jobs(jobs)

if filtered:
    df = pd.DataFrame(filtered)
    df.to_csv(OUT_CSV, index=False)

    EMAIL_TO = os.getenv("JOB_EMAIL_TO")
    EMAIL_FROM = os.getenv("JOB_EMAIL_FROM")
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    msg = EmailMessage()
    msg["Subject"] = f"New Startup Jobs Found ({len(filtered)})"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(df.to_csv(index=False))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

    print("Email sent.")
else:
    print("No new jobs found.")
