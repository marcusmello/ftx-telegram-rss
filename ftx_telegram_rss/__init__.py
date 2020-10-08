__version__ = '0.1.0'

import requests

def get_response(endpoint: str):
    with requests.get(endpoint) as response:
        if response.status_code == 200:
            return response


def get_listed_futures_names()->list:

    endpoint = "https://ftx.com/api/futures"

    futures = (get_response(endpoint)).json()

    return [
        future['name'] for
        future in futures['result']
    ]