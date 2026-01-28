"""Main entry point for bike alert system"""
import logging
import time
from change_data_capture import get_new_listing_urls
from scraper import fetch_and_parse_listing
from llm_classifier import BikeClassifier
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


# TODO: Figure out how env var loading works in the cloud

def main():
    """Run the full bike alert pipeline"""
    log.info("🔍 Starting bike alert check...")

    # load our config
    config: Config = Config()

    # 1. Get new listings via CDC
    try:
        new_urls = get_new_listing_urls(n_minutes=config.check_interval_minutes)
    except Exception as e:
        log.error(f"Failed to fetch new listings: {e}", exc_info=True)
        return

    if not new_urls:
        log.info(f"No new listings found in the past {config.check_interval_minutes} minutes ")
        return

    log.info(f"Found {len(new_urls)} new listings to check")

    # 2. Initialize classifier
    classifier = BikeClassifier(api_key=config.anthropic_api_key)

    good_bikes_found = 0

    # 3. Process each listing
    for i, url in enumerate(new_urls, 1):
        log.info(f"\n[{i}/{len(new_urls)}] Processing: {url}")

        # Parse listing
        listing = fetch_and_parse_listing(url)
        if not listing:
            log.warning(f"Failed to parse listing: {url}")
            continue

        log.info(f"  Title: {listing.title}")
        log.info(f"  Price: {listing.price}")
        log.info(f"  Type: {listing.bicycle_type}")

        # Classify
        try:
            is_good, reason = classifier.classify(listing)

            if is_good:
                log.info(f"GOOD BIKE FOUND! Reason: {reason}")
                good_bikes_found += 1

                # TODO: Send SMS alert
            else:
                log.info(f"Rejected: {reason}")

        except Exception as e:
            log.error(f"Failed to classify: {e}")

        # Rate limiting - be nice to Craigslist
        time.sleep(2)

    log.info(f"\nCheck complete! Found {good_bikes_found} good bikes out of {len(new_urls)} new listings")


if __name__ == "__main__":
    main()
