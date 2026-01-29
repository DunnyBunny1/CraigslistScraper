"""Main entry point for bike alert system"""

import logging
import time

from change_data_capture import get_new_listing_urls
from config import Config
from llm_classifier import BikeClassifier, BikeClassification
from notifier import send_whatsapp_alert
from scraper import fetch_and_parse_listing
import functions_framework

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


@functions_framework.http
def check_new_bikes(request):
    """Cloud Function HTTP entry point"""
    log.info("Cloud Function triggered")
    try:
        run_pipeline()
        return "Bike check completed successfully", 200
    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)
        return f"Error: {str(e)}", 500


def run_pipeline():
    """Run the full bike alert pipeline"""
    log.info("Starting bike alert check...")

    # load our config
    config: Config = Config()

    # 1. Get new the URLS for any new listings since we last ran this program
    try:
        new_urls = get_new_listing_urls(n_minutes=config.check_interval_minutes)
    except Exception as e:
        log.error(f"Failed to fetch new listings: {e}", exc_info=True)
        return

    if not new_urls:
        log.info(
            f"No new listings found in the past {config.check_interval_minutes} minutes"
        )
        return

    log.info(f"Found {len(new_urls)} new listings to check")

    # 2. Initialize classifier
    classifier = BikeClassifier(api_key=config.anthropic_api_key)

    good_bikes_found = 0
    high_confidence_matches = 0

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

        # classify the listing using our LLM
        try:
            classification: BikeClassification = classifier.classify(listing)

            if classification.is_good:
                log.info(f"GOOD BIKE FOUND!")
                log.info(f"\tReason: {classification.reason}")
                log.info(f"\tConfidence: {classification.confidence}")
                log.info(f"\tURL: {url}")

                good_bikes_found += 1

                if classification.confidence == "high":
                    high_confidence_matches += 1
                    # send whatsapp alerts for high-confidence matches
                    send_whatsapp_alert(listing, classification.reason)
            else:
                log.info(
                    f"Rejected ({classification.confidence}): {classification.reason}"
                )

        except Exception as e:
            log.error(f"Failed to classify: {e}", exc_info=True)

        # simple rate limiting - TODO refactor to use tenacity library for rate limmiting + retries
        time.sleep(2)

    # Summary
    log.info(f"\n{'=' * 60}")
    log.info(f"Check complete!")
    log.info(f"\tTotal new listings: {len(new_urls)}")
    log.info(f"\tGood bikes found: {good_bikes_found}")
    log.info(f" \tHigh-confidence matches: {high_confidence_matches}")
    log.info(f"{'=' * 60}")


if __name__ == "__main__":
    run_pipeline()
