import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from models import BikeListingData

log = logging.getLogger(__name__)


class BikeClassification(BaseModel):
    """Structured output for bike classification."""

    is_good: bool = Field(description="Whether this is a good bike deal")
    reason: str = Field(description="One-sentence explanation for the classification")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")


class BikeClassifier:
    """
    LLM client for classifying Craigslist bike listings as good or bad deals.
    Uses few-shot prompting with diverse examples and structured output.
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
        ).with_structured_output(
            BikeClassification
        )  # attach our structured output for pydantic validation on the LLM response

        self.system_prompt = """You are a bike expert who identifies quality MODERN road bikes on Craigslist.

YOUR TASK:
Classify bikes as good or bad deals. Return a structured classification with is_good, reason, and confidence ("high", "medium", or "low").

GOOD BIKES MUST HAVE ALL:
- Type: Road bike (NOT hybrid, mountain, cruiser, e-bike, BMX)
- Components: MODERN Shimano 105+ (10/11-speed Ultegra/Dura-Ace) OR SRAM Rival/Force/Red
- Brand: Quality (Cannondale, Trek, Specialized, Giant, Cervelo, Bianchi, etc.)
- Frame: Carbon or high-quality aluminum
- Era: Modern (NOT 1970s-1990s vintage, even with period-correct quality components)

AUTO-REJECT ANY OF:
- Wrong type, e-bikes, low-end components (Sora/Claris/Tourney/Tiagra), vague components
- Vintage bikes from 1970s-1990s (outdated tech even if quality brands/components)
- Department store brands, not ride-ready, no component details, outside price range

EXAMPLES:

Example 1 - GOOD MODERN BIKE:
Title: "50cm Cannondale SuperSix EVO Ultegra Di2"
Price: $1,875
Bicycle Type: road
Frame Material: carbon fiber
Manufacturer: Cannondale
Description: Shimano Ultegra Di2 2x11speed electronic shifting groupset, carbon wheels

Classification: 
{"is_good": true, "reason": "Premium carbon road bike with modern Ultegra Di2 at fair price", "confidence": "high"}

Example 2 - WRONG TYPE:
Title: "Trek FX3 Hybrid - Great Condition"
Price: $600
Bicycle Type: hybrid
Frame Material: aluminum
Manufacturer: Trek
Description: Excellent commuter bike, well maintained

Classification:
{"is_good": false, "reason": "This is a hybrid bike, not a road bike", "confidence": "high"}

Example 3 - VINTAGE (OUTDATED):
Title: "Schwinn Waterford Paramount 59cm"
Price: $750
Bicycle Type: road
Frame Material: steel
Manufacturer: Schwinn
Description: Shimano 600 components, 7-speed, downtube shifters, 1980s era

Classification:
{"is_good": false, "reason": "Vintage 1980s bike with outdated 7-speed groupset, not modern 10/11-speed 105+", "confidence": "high"}

Example 4 - GOOD ENTRY-LEVEL:
Title: "54cm Trek Emonda SL5 - Shimano 105"
Price: $1,200
Bicycle Type: road
Frame Material: carbon fiber
Manufacturer: Trek
Description: Full Shimano 105 11-speed groupset, carbon frame, excellent condition, ready to ride

Classification:
{"is_good": true, "reason": "Quality carbon road bike with modern Shimano 105 11-speed at reasonable price", "confidence": "high"}

Example 5 - VAGUE/INCOMPLETE:
Title: "Carbon Road Bike - Great Deal!"
Price: $1,500
Bicycle Type: road
Frame Material: carbon fiber
Manufacturer: Unknown
Description: Nice carbon road bike, rides great, Shimano components

Classification:
{"is_good": false, "reason": "Vague listing with no specific component details or brand information", "confidence": "medium"}

Now classify the following bike:"""

    def classify(self, listing: BikeListingData) -> BikeClassification:
        """
        Classify a bike listing as good or bad based on quality criteria.

        :param listing: Parsed BikeListingData object
        :return: BikeClassification object with is_good, reason, and confidence
        """
        # Build a structured prompt matching the example format
        user_message = f"""Title: "{listing.title}"
Price: {listing.price or "Not listed"}
Bicycle Type: {listing.bicycle_type or "Unknown"}
Frame Size: {listing.frame_size or "Not specified"}
Frame Material: {listing.frame_material or "Unknown"}
Wheel Size: {listing.wheel_size or "Unknown"}
Manufacturer: {listing.manufacturer or "Unknown"}
Model: {listing.model or "Unknown"}
Condition: {listing.condition or "Not specified"}
Description: {listing.body[:500]}{"..." if len(listing.body) > 500 else ""}

Classification:"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message),
        ]

        # Call the LLM with structured output
        log.info(f"Classifying: {listing.title}")
        classification: BikeClassification = self.llm.invoke(messages)

        log.info(
            f"Classification result: is_good={classification.is_good}, "
            f"confidence={classification.confidence}, reason={classification.reason}"
        )

        return classification

    def classify_batch(
            self, listings: list[BikeListingData]
    ) -> list[tuple[BikeListingData, BikeClassification]]:
        """
        Classify multiple listings efficiently.

        :param listings: List of BikeListingData objects
        :return: List of tuples (listing, classification)
        """
        results = []

        for listing in listings:
            try:
                classification = self.classify(listing)
                results.append((listing, classification))
            except Exception as e:
                log.error(f"Failed to classify {listing.url}: {e}")
                # Create a failed classification object
                failed_classification = BikeClassification(
                    is_good=False,
                    reason=f"Classification failed: {str(e)}",
                    confidence="low",
                )
                results.append((listing, failed_classification))

        return results
