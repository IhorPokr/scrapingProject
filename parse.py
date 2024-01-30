import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://webscraper.io/"
HOME_URL = BASE_URL + "test-sites/e-commerce/allinone"


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int


def parse_single_product(product_soup: BeautifulSoup) -> Product:
    return Product(
        title=product_soup.select_one(".title")["title"],
        description=product_soup.select_one(".description").text,
        price=float(product_soup.select_one(".price").text.replace("$", "")),
        rating=int(product_soup.select_one("p[data-rating]")["data-rating"]),
    )


def get_home_products() -> [Product]:
    page = requests.get(HOME_URL).content
    soup = BeautifulSoup(page, "html.parser")

    products = soup.select(".thumbnail")

    return [parse_single_product(product_soup) for product_soup in products]


def write_products_to_csv(products: [Product]):
    """Writes a list of products to a CSV file."""

    with open("products.csv", "w", newline="") as csvfile:
        fieldnames = ["title", "description", "price", "rating"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product in products:
            writer.writerow(product.__dict__)


def main():
    products = get_home_products()
    write_products_to_csv(products)


if __name__ == '__main__':
    main()
