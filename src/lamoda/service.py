import json

import requests
from bs4 import BeautifulSoup
from fastapi.exceptions import HTTPException

from .config import LamodaSettings
from .schemas import LamodaProduct, LamodaCategory

settings = LamodaSettings()
lamoda_url = settings.lamoda_url


def parse_lamoda_category(url: str) -> LamodaCategory:
    """Function that provides parsing of lamoda category"""

    category_info = get_info_to_parse_category(url)
    parsed_objects = [
        parse_object(lamoda_url + link) for link in category_info["links"]
    ]
    category = LamodaCategory(
        category_title=category_info["title"],
        products=parsed_objects,
        url=url,
    )
    return category


def get_info_to_parse_category(url: str) -> dict:
    """Function that takes all product urls from category"""

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    product_cards = soup.find_all("div", class_="x-product-card__card")
    category_info = {
        "title": soup.find("h1", class_="d-catalog-header__title-text").text.replace(
            "\n", ""
        ),
        "links": [],
    }
    for product in product_cards:
        links = product.find_all(
            "a", class_="x-product-card__link x-product-card__hit-area", href=True
        )
        for link in links:
            category_info["links"].append(link.attrs["href"])
    return category_info


def parse_object(url: str) -> LamodaProduct:
    """Function that creates a LamodaProduct object by parsing url"""

    response = requests.get(url)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="No such lamoda item")
    soup = BeautifulSoup(response.text, "html.parser")
    object_card = soup.find_all("script")
    for script in object_card:
        target_variable = "__NUXT__"
        if target_variable in script.text:
            state_var_pos = script.text.find("state")
            state_var_text = script.text[state_var_pos:]
            payload_var_pos = state_var_text.find("payload")
            payload_var_text = state_var_text[payload_var_pos:]
            target_dict_start = payload_var_text.find("{")
            target_dict_end = payload_var_text.find("\n")

            target_dict = payload_var_text[target_dict_start : target_dict_end - 1]
            full_result_dict = from_script_to_dict(target_dict)
            result_dict = full_result_dict["product"]
            model_from_dict = LamodaProduct.parse_obj(
                {
                    "product_sku": result_dict["sku"],
                    "product_type": result_dict["type"],
                    "product_title": result_dict["title"],
                    "brand": result_dict["brand"]["title"],
                    "price": result_dict["prices"]["original"]["price"].replace(
                        " ", ""
                    ),
                    "attributes": result_dict["attributes"],
                    "url": url,
                }
            )
            return model_from_dict


def remove_redundant_quotes(string_to_refactor: str) -> str:
    """Function to remove redundant quotes like {"owner": "OOO \"Products"\"}"""

    expected_after_quotes = ["{", "}", ",", ":", "]", "["]
    opened = False
    to_replace = []
    for el_id, el in enumerate(string_to_refactor):
        if el == '"' and not opened:
            opened = True
            continue
        if el == '"' and opened:
            if string_to_refactor[el_id + 1] not in expected_after_quotes:
                to_replace.append(el_id)
            else:
                opened = False
    for replace in to_replace:
        string_to_refactor = (
            string_to_refactor[:replace] + "'" + string_to_refactor[replace + 1 :]
        )
    return string_to_refactor


def refactor_to_python_dict(string_to_refactor: str) -> str:
    """Function that changes JS-key words to python"""

    string_to_refactor = string_to_refactor.replace("false", '''"False"''')
    string_to_refactor = string_to_refactor.replace("true", '''"True"''')
    string_to_refactor = string_to_refactor.replace("null", '''"None"''')
    #  soon will change to provides all changes by one iteration
    return string_to_refactor


def from_script_to_dict(string_from_script: str) -> dict:
    """Function that refactors text from JS-script to python dict"""

    string_from_script = string_from_script.replace(r"\"", "'")
    string_from_script = refactor_to_python_dict(string_from_script)
    string_from_script = string_from_script.replace("\\", "")
    return json.loads(string_from_script)
