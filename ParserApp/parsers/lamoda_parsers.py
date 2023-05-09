import requests
from bs4 import BeautifulSoup

lamoda_domen = "https://www.lamoda.by"


def parse_category(url: str) -> list:
    links = get_links_to_parse_category(url)
    parsed_objects = [parse_object(lamoda_domen + link) for link in links]
    return parsed_objects


def get_links_to_parse_category(url: str) -> list:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    product_cards = soup.find_all("div", class_="x-product-card__card")
    links_to_parse = []
    for product in product_cards:
        links = product.find_all(
            "a", class_="x-product-card__link x-product-card__hit-area", href=True
        )
        for link in links:
            links_to_parse.append(link.attrs["href"])
    return links_to_parse


def parse_object(url: str) -> dict:
    response = requests.get(url)
    if response.status_code == 404:
        return "Page does not exists"  # Process if there is no such page
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

            target_dict = payload_var_text[target_dict_start:target_dict_end - 1]
            result_dict = from_script_to_dict(target_dict)
            return result_dict["product"]


def remove_redundant_quotes(string_to_refactor: str) -> str:
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
            string_to_refactor[:replace] + "'" + string_to_refactor[replace + 1:]
        )
    return string_to_refactor


def refactor_to_python_dict(string_to_refactor: str) -> str:
    string_to_refactor = string_to_refactor.replace("false", "False")
    string_to_refactor = string_to_refactor.replace("true", "True")
    string_to_refactor = string_to_refactor.replace("null", "None")
    return string_to_refactor


def from_script_to_dict(string_from_script: str) -> dict:
    string_from_script = remove_redundant_quotes(string_from_script)
    string_from_script = refactor_to_python_dict(string_from_script)
    return eval(string_from_script)
