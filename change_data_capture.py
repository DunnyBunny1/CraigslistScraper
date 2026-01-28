"""Change Data Capture for Craigslist bike listings"""
import requests
import time
from typing import List


def fetch_active_listings_until(timestamp: int) -> dict:
    """
    Fetch all bike listings posted until the given timestamp that still exist.

    :param timestamp: Unix epoch timestamp
    :return: JSON response from Craigslist API
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0',
        'Accept': 'application/json',
    }

    params = {
        'batch': f'1-{timestamp}-0-1-0',
        'lat': '37.789',
        'lon': '-122.394',
        'searchPath': 'san-francisco-ca/bia',
        'search_distance': '15',
        'lang': 'en',
        'cc': 'us',
    }

    response = requests.get(
        'https://sapi.craigslist.org/web/v8/postings/search/full',
        params=params,
        headers=headers,
        timeout=10
    )
    return response.json()


def get_new_listing_urls(n_minutes: int) -> List[str]:
    """
    Get URLs of new bike listings from the last N minutes.

    :param n_minutes: Number of minutes to look back
    :return: List of URLs for new listings
    """
    now = int(time.time())
    n_minutes_ago = now - (n_minutes * 60)

    # Request 1: State N minutes ago
    old_listings = fetch_active_listings_until(n_minutes_ago)
    old_items = old_listings['data']['items']
    old_ids = {item[0] for item in old_items}

    # Request 2: Current state
    curr_listings = fetch_active_listings_until(now)
    curr_items = curr_listings['data']['items']

    # Find truly new listings
    new_items = [item for item in curr_items if item[0] not in old_ids]

    print(f"Old listing count: {len(old_ids)}")
    print(f"Current listing count: {len(curr_items)}")
    print(f"New listings in past {n_minutes} minutes: {len(new_items)}")

    # Decode the listings to get URLs
    min_posting_id = curr_listings['data']['decode']['minPostingId']
    sf_bikes_url_base = "https://sfbay.craigslist.org/bik/"

    return [
        f"{sf_bikes_url_base}{min_posting_id + item[0]}.html"
        for item in new_items
    ]
