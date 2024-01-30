import csv
from dataclasses import dataclass
import logging
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://webscraper.io/"
HOME_URL = BASE_URL + "test-sites/e-commerce/allinone"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)8s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)  # Get a logger for this module


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int


def parse_single_product(product_soup: BeautifulSoup) -> Product:
    logger.debug("Parsing product: %s", product_soup)
    return Product(
        title=product_soup.select_one(".title")["title"],
        description=product_soup.select_one(".description").text,
        price=float(product_soup.select_one(".price").text.replace("$", "")),
        rating=int(product_soup.select_one("p[data-rating]")["data-rating"]),
    )


def get_home_products() -> [Product]:
    logger.info("Fetching home page products")
    page = requests.get(HOME_URL).content
    soup = BeautifulSoup(page, "html.parser")

    products = soup.select(".thumbnail")

    if not products:
        logger.warning("No products found on the home page")

    return [parse_single_product(product_soup) for product_soup in products]


def write_products_to_csv(products: [Product]):
    """Writes a list of products to a CSV file."""

    logger.info("Writing products to CSV file")
    with open("products.csv", "w", newline="") as csvfile:
        fieldnames = ["title", "description", "price", "rating"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product in products:
            writer.writerow(product.__dict__)


def main():
    logger.info("Starting product scraping and parsing")
    products = get_home_products()
    write_products_to_csv(products)
    logger.info("Finished successfully")


if __name__ == '__main__':
    main()
