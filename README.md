# CraigslistScraper

An automated program to scrape Craiglist and send phone notifications on interesting listings. Currently
used to detect Shimano-quality roadbikes sold within 15 miles of San Francisco


## System Design 
```
Every 15 minutes
─────────────────────────────────────────────────────────────────────────────

┌───────────────────────────────┐
│        Cloud Scheduler        │
│   Cron: */15 * * * *          │
│                               │
│  Triggers HTTP invocation     │
└───────────────┬───────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Google Cloud Function (Serverless)                      │
│                          bike-alert-checker                                 │
│                                                                             │
│  ┌──────────────────────────┐                                               │
│  │ 1. Change Data Capture   │                                               │
│  │                          │                                               │
│  │ - Query Craigslist API   │──────────────▶ Craigslist SAPI (JSON)         │
│  │ - Diff now vs -15 min    │                                               │
│  │ - Output: listing IDs   │                                                │
│  └──────────────┬───────────┘                                               │
│                 │                                                           │
│                 │  (IDs of new listings)                                    │
│                 ▼                                                           │
│  ┌──────────────────────────┐                                               │
│  │ 2. HTML Scraper          │                                               │
│  │                          │                                               │
│  │ - Fetch HTML per ID      │──────────────▶ Craigslist Listings (HTML)     │
│  │ - Parse title, price     │                                               │
│  │ - Extract bike specs     │                                               │
│  └──────────────┬───────────┘                                               │
│                 │                                                           │
│                 ▼                                                           │
│  ┌──────────────────────────┐        ┌──────────────────────────────────┐   │
│  │ 3. LLM Classifier        │──────▶ │      Anthropic Claude API        │   │
│  │                          │        │        (Sonnet 3.5)              │   │
│  │ - Few-shot prompt        │        │       Binary Classification:     │   │ 
│  │ - Evaluate bike quality  │        │  Quality (1)or Not Quality  (0)  │   │
│  └──────────────┬───────────┘        └──────────────────────────────────┘   │
│                 │                                                           │
│                 ▼                                                           │
│  ┌──────────────────────────┐        ┌──────────────────────────────────┐   │
│  │ 4. WhatsApp Notifier     │──────▶ │        Twilio WhatsApp API       │   │
│  │                          │        │          (Sandbox)               │   │
│  │ - Format alert           │        │                                  │   │
│  │ - Send message           │        │  Delivers WhatsApp message       │   │
│  └──────────────────────────┘        └──────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                          ┌────────────────────┐
                          │  📱 WhatsApp User  │
                          │  Push Notification │
                          └────────────────────┘
```

## Overview

This system runs every 15 minutes to:

1. **Detect new listings** using Change Data Capture (CDC)
2. **Scrape listing details** from Craigslist HTML
3. **Classify bikes** using Claude AI (LLM)
4. **Send WhatsApp alerts** for high-quality matches 

## Features

- **Stateless CDC** - Detects new listings without maintaining state
- **LLM Classification** - Uses Anthropic Claude to identify quality bikes
- **WhatsApp Notifications** - Instant alerts via Twilio
**CI/CD Pipeline** - Automatic deployment via GitHub Actions
**Serverless** - Runs on Google Cloud Functions

## Tech Stack

- **Python 3.12**
- **Anthropic Claude API** - LLM for bike classification
- **Twilio WhatsApp** - Push notifications
- **BeautifulSoup** - HTML parsing
- **Google Cloud Functions** - Serverless compute
- **Google Cloud Scheduler** - Cron jobs
- **GitHub Actions** - CI/CD


## Project Structure

```
.
├── src/
│   ├── main.py                    # Entry point & pipeline orchestration
│   ├── change_data_capture.py     # CDC logic for new listings
│   ├── scraper.py                 # HTML parsing
│   ├── llm_classifier.py          # Claude-based classification
│   ├── notifier.py                # WhatsApp notifications
│   ├── models.py                  # Pydantic data models
│   ├── config.py                  # Configuration
│   └── requirements.txt           # Dependencies
├── .github/workflows/deploy.yml   # CI/CD pipeline
└── README.md
```

## Setup

### Prerequisites

- Python 3.12+
- Anthropic API key
- Twilio account (WhatsApp sandbox)
- Google Cloud account

### Local Development

1. **Clone and install:**

```bash
git clone https://github.com/YOUR_USERNAME/CraigslistScraper.git
cd CraigslistScraper
pip install -r src/requirements.txt
```

2. **Configure environment:**

```bash
# copy the env var file
cp .env_template .env 
# <add your environment variables> 
```

3. **Join WhatsApp sandbox:**

- Text `join <code>` to +1 (415) 523-8886 on whatsapp
- Get code from: https://console.twilio.com/whatsapp-learn

4. **Run locally:**

```bash
python src/main.py
```

## How It Works

### 1. Change Data Capture (CDC)

Queries Craigslist API at two timestamps (now and 15 min ago) to find new listings:

```python
old_listings = fetch_listings(now - 15min)
new_listings = fetch_listings(now)
diff = new_listings - old_listings  # These are new!
```

### 2. HTML Parsing

Scrapes bike details from Craigslist HTML:

- Title, price, description
- Frame size, material, wheel size
- Bike type, condition, manufacturer

### 3. LLM Classification

Uses Claude with few-shot prompting to identify quality bikes:

- **Good:** Road bikes with Shimano 105+ components
- **Bad:** E-bikes, cruisers, low-end components

### 4. WhatsApp Notification

Sends alerts for high-confidence matches:

```
🚴 Good Bike Found!

2019 Trek Domane - $850

Quality Trek road bike with Shimano 105 
components at fair price

https://sfbay.craigslist.org/...
```

## Configuration

Edit `src/config.py` to change:

- Search location (lat/lon)
- Search radius (miles)
- Check interval (minutes)

## CI/CD Pipeline

GitHub Actions automatically:

1. Authenticates with Google Cloud
2. Deploys code to Cloud Functions
3. Updates environment variables

**Trigger:** Every push to `main` branch

## Cloud monitoring
To run, view, debug, or edit this project, visit the google cloud console
https://console.cloud.google.com/functions