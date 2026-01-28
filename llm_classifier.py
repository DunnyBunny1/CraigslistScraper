import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from models import BikeListingData

log = logging.getLogger(__name__)


class BikeClassifier:
    """
    LLM client for classifying Craigslist bike listings as good or bad deals.
    Uses structured BikeListingData for accurate classification.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        """
        Initialize the bike classifier.

        :param api_key: Anthropic API key
        :param model: Claude model to use
        """
        self.llm = ChatAnthropic(
            api_key=api_key,
            model=model,
            temperature=0.0,  # Deterministic for consistent classifications
        )

        self.system_prompt = """You are a bike expert who identifies quality road bikes on Craigslist.

WHAT I'M LOOKING FOR:
- Road bikes with quality components (Shimano 105 or better: Ultegra, Dura-Ace, SRAM Rival/Force/Red)
- Quality brands: Cannondale, Trek, Specialized, Giant, Cervelo, Bianchi, etc.
- Carbon fiber or high-quality aluminum frames
- Good condition, complete bikes ready to ride
- Reasonable prices: $800-$3000 for used

EXAMPLE OF A GOOD BIKE:
Title: "50cm Cannondale SuperSix EVO Hi-Mod Ultegra Di2 22speed road bike"
Price: $1,875
Type: road
Frame: 50cm carbon fiber
Manufacturer: Cannondale
Model: SuperSix EVO Hi-Mod
Description: "Shimano Ultegra Di2 2x11speed electronic shifting groupset... retailed around $5200"
WHY GOOD: Premium carbon road bike from quality brand, Ultegra Di2 components (better than 105), fair price for high-end bike

EXAMPLE OF A BAD BIKE:
Title: "Scott Silence ERide 10"
Price: $950
Type: cruiser
Frame: aluminum
Manufacturer: Scott
Model: Silence ERide
Description: "ebike... has not been used much"
WHY BAD: This is an e-bike cruiser, not a road bike. Wrong type completely.

REJECT THESE:
- E-bikes (electric bikes)
- Cruisers, comfort bikes, hybrids, mountain bikes, BMX
- Low-end components (Shimano Sora, Claris, Tourney, or unspecified)
- Department store brands (Schwinn, Huffy, etc.)
- Broken bikes, parts only, project bikes
- Vague descriptions with no component details
- Kids bikes

YOUR TASK:
Respond with ONLY "GOOD" or "BAD" followed by a one-sentence reason.

Focus on:
1. Is it a ROAD bike? (not cruiser, hybrid, comfort, mountain, e-bike)
2. Does it have quality components? (105+ or equivalent mentioned)
3. Is it a known quality brand?
4. Is the price reasonable for what it is?"""

    def classify(self, listing: BikeListingData) -> tuple[bool, str]:
        """
        Classify a bike listing as good or bad based on quality criteria.

        :param listing: Parsed BikeListingData object
        :return: (is_good: bool, reason: str)
        """
        # Build a focused prompt with all available structured data
        user_message = f"""Title: {listing.title}
Price: {listing.price or 'Not listed'}
Bicycle Type: {listing.bicycle_type or 'Unknown'}
Frame Size: {listing.frame_size or 'Not specified'}
Frame Material: {listing.frame_material or 'Unknown'}
Wheel Size: {listing.wheel_size or 'Unknown'}
Manufacturer: {listing.manufacturer or 'Unknown'}
Model: {listing.model or 'Unknown'}
Condition: {listing.condition or 'Not specified'}

Description: {listing.body[:500]}{"..." if len(listing.body) > 500 else ""}

Classify this bike:"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]

        # Call the LLM
        log.info(f"Classifying: {listing.title}")
        response = self.llm.invoke(messages)

        # Extract the text response
        answer = response.content
        log.info(f"Classification result: {answer}")

        # Parse response - check if first word is "GOOD"
        is_good = answer.strip().upper().startswith("GOOD")

        return is_good, answer

    def classify_batch(self, listings: list[BikeListingData]) -> list[tuple[BikeListingData, bool, str]]:
        """
        Classify multiple listings efficiently.

        :param listings: List of BikeListingData objects
        :return: List of tuples (listing, is_good, reason)
        """
        results = []

        for listing in listings:
            try:
                is_good, reason = self.classify(listing)
                results.append((listing, is_good, reason))
            except Exception as e:
                log.error(f"Failed to classify {listing.url}: {e}")
                results.append((listing, False, f"Classification failed: {e}"))

        return results
