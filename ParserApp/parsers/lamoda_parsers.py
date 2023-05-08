from bs4 import BeautifulSoup
import requests
from pprint import pprint

url = "https://www.lamoda.by/p/pu053bucjht0/bags-puma-ryukzak/"


def parse_object():
    response = requests.get(url)
    if response.status_code == 404:
        return "Page does not exists"
    soup = BeautifulSoup(response.text, "html.parser")
    object_card = soup.find_all("script")
    for script in object_card:
        target_variable = "__NUXT__"
        if target_variable in script.text:
            state_var_pos = script.text.find('state')
            state_var_text = script.text[state_var_pos:]
            payload_var_pos = state_var_text.find("payload")
            payload_var_text = state_var_text[payload_var_pos:]
            target_dict_start = payload_var_text.find('{')
            target_dict_end = payload_var_text.find('\n')
            target_dict = payload_var_text[target_dict_start: target_dict_end-1]
            result_dict = from_script_to_dict(target_dict)
            pprint(result_dict)


def remove_redundant_quotes(string_to_refactor: str) -> str:
    expected_after_quotes = ['{', '}', ",", ":", "]", "["]
    opened = False
    to_replace = []
    for el_id, el in enumerate(string_to_refactor):
        if el == '"' and not opened:
            opened = True
            continue
        if el == '"' and opened:
            if string_to_refactor[el_id+1] not in expected_after_quotes:
                to_replace.append(el_id)
            else:
                opened = False
    for replace in to_replace:
        string_to_refactor = string_to_refactor[:replace]+"'"+string_to_refactor[replace+1:]
    return string_to_refactor


def refactor_to_python_dict(string_to_refactor: str) -> str:
    string_to_refactor = string_to_refactor.replace('false', 'False')
    string_to_refactor = string_to_refactor.replace('true', 'True')
    string_to_refactor = string_to_refactor.replace('null', 'None')
    return string_to_refactor


def add_extra_quotes(string_to_refactor: str):
    tech_symbols = ['{', '}', ",", ":", "]", "["]
    quotes = ['"', "'"]
    string_len = len(string_to_refactor)
    to_add = []
    for el_id, el in enumerate(string_to_refactor):
        if el in tech_symbols:
            if el_id != string_len-1 and string_to_refactor[el_id+1] not in quotes+tech_symbols:
                start_point = el_id+1
                while string_to_refactor[start_point] not in tech_symbols:
                    start_point += 1
                else:
                    to_add.append((el_id, start_point))
    for add in to_add:
        for cord in add:
            string_to_refactor = string_to_refactor[:cord+1]+"'"+string_to_refactor[cord+1:]
    return string_to_refactor


def from_script_to_dict(string_from_script):
    string_from_script = remove_redundant_quotes(string_from_script)
    string_from_script = refactor_to_python_dict(string_from_script)
    return eval(string_from_script)


parse_object()
