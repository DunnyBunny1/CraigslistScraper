from bs4 import BeautifulSoup
from typing import Optional
import requests
from models import BikeListingData


def parse_craigslist_bike_listing(html: str, url: str) -> BikeListingData:
    """
    Parse a Craigslist bike listing HTML page and extract structured data.

    :param html: Raw HTML content of the listing page
    :param url: URL of the listing
    :return: BikeListingData model with extracted fields
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title_elem = soup.select_one("span#titletextonly")
    title = title_elem.get_text(strip=True) if title_elem else "No title"

    # Extract price
    price_elem = soup.select_one("span.price")
    price = price_elem.get_text(strip=True) if price_elem else None

    # Extract body content
    body_elem = soup.select_one("section#postingbody")
    if body_elem:
        # Remove QR code container
        for qr in body_elem.select("div.print-qrcode-container"):
            qr.decompose()
        # Get text and clean up <br> tags
        body = body_elem.get_text(separator=" ", strip=True)
        # Clean up excessive whitespace
        body = " ".join(body.split())
    else:
        body = "No description"

    # Extract attributes from the .attr divs
    def extract_attr(attr_class: str) -> Optional[str]:
        """Helper to extract attribute value from div with specific class"""
        attr_div = soup.select_one(f"div.attr.{attr_class}")
        if attr_div:
            valu_elem = attr_div.select_one("span.valu")
            if valu_elem:
                # Get text, removing any <a> tag but keeping the text inside
                return valu_elem.get_text(strip=True)
        return None

    bicycle_type = extract_attr("bicycle_type")
    wheel_size = extract_attr("bicycle_wheel_size")
    frame_size = extract_attr("bicycle_frame_size_freeform")
    frame_material = extract_attr("bicycle_frame_material")
    manufacturer = extract_attr("sale_manufacturer")
    model = extract_attr("sale_model")
    condition = extract_attr("condition")

    return BikeListingData(
        title=title,
        price=price,
        bicycle_type=bicycle_type,
        wheel_size=wheel_size,
        frame_size=frame_size,
        frame_material=frame_material,
        manufacturer=manufacturer,
        model=model,
        condition=condition,
        body=body,
        url=url,
    )


def fetch_and_parse_listing(url: str) -> Optional[BikeListingData]:
    """
    Fetch a Craigslist listing and parse it into structured data.

    :param url: URL of the Craigslist bike listing
    :return: BikeListingData or None if fetch fails
    """
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            timeout=10,
        )

        if response.status_code == 200:
            return parse_craigslist_bike_listing(response.text, url)
        else:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return None

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
