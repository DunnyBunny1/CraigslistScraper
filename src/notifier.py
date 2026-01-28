"""SMS/WhatsApp notifications via Twilio"""

import logging

from twilio.rest import Client

from config import Config
from models import BikeListingData

# shared phone number to use as the "from" phone number for any messages sent by twilio over whatsapp
TWILIO_WHATSAPP_SANDBOX_NUMBER: str = "whatsapp:+14155238886"

log = logging.getLogger(__name__)

# load our config
config = Config()


def send_whatsapp_alert(listing: BikeListingData, reason: str) -> bool:
    """
    Send WhatsApp alert for a good bike listing.

    :param listing: BikeListingData object
    :param reason: Classification reason from LLM
    :return: True if sent successfully
    """
    if not config.twilio_account_sid or not config.twilio_auth_token:
        log.warning("Twilio not configured - skipping WhatsApp")
        return False

    try:
        client = Client(config.twilio_account_sid, config.twilio_auth_token)

        # Build message, ensuring to include the URL to the relevant listing post
        message_body = f"""🚴 *Good Bike Found!*

*{listing.title}*
{listing.price or "Price not listed"}

{reason[:150]}

{listing.url}"""

        # Send WhatsApp using sandbox
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_SANDBOX_NUMBER,  # Twilio WhatsApp sandbox
            to=f"whatsapp:{config.twilio_to_number}",
        )

        log.info(f"WhatsApp sent successfully: {message.sid}")
        return True

    except Exception as e:
        log.error(f"Failed to send WhatsApp: {e}")
        return False
