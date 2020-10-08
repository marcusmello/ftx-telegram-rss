__version__ = '0.1.0'

import requests

def get_response(endpoint: str):
    with requests.get(endpoint) as response:
        if response.status_code == 200:
            return response


def get_instruments_names_list():

    endpoint = "https://ftx.com/api/futures"

    instruments = (get_response(endpoint)).json()

    return [
        instrument['name'] for
        instrument in instruments['result']
    ]