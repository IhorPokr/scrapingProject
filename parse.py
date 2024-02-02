import csv
from dataclasses import dataclass
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


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
    additional_info: dict


def parse_hdd_block_prices(product_soup: BeautifulSoup) -> dict[str, float]:
    detailed_url = urljoin(BASE_URL, product_soup.select_one(".title")["href"])
    driver = webdriver.Chrome()  # TODO: fix this bad practice - move it to init step
    driver.get(detailed_url)
    swatches = driver.find_element(By.CLASS_NAME, "swatches")
    buttons = swatches.find_elements(By.TAG_NAME, "button")

    prices = {}

    for button in buttons:
        if not button.get_property("disabled"):
            button.click()
            prices[button.get_property("value")] = float(driver.find_element(
                By.CLASS_NAME, "price"
            ).text.replace("$", ""))

    driver.close()

    return prices


def parse_single_product(product_soup: BeautifulSoup) -> Product:
    logger.debug("Parsing product: %s", product_soup)

    hdd_prices = parse_hdd_block_prices(product_soup)

    return Product(
        title=product_soup.select_one(".title")["title"],
        description=product_soup.select_one(".description").text,
        price=float(product_soup.select_one(".price").text.replace("$", "")),
        rating=int(product_soup.select_one("p[data-rating]")["data-rating"]),
        additional_info={"hdd_prices": hdd_prices},
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
