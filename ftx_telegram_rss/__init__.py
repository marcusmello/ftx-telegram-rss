__version__ = "0.1.0"

import requests


class Future:
    name = None
    funding_rate = None


def get_response(endpoint: str):
    with requests.get(endpoint) as response:
        if response.status_code == 200:
            return response


def get_all_listed_futures_names() -> list:

    endpoint = "https://ftx.com/api/futures"

    futures = (get_response(endpoint)).json()

    return [future["name"] for future in futures["result"]]


_endpoint = "https://ftx.com/api//futures/{}/stats"


def make_future(name) -> Future:
    future = Future()
    future.name = name

    future_dict = (get_response(_endpoint.format(name))).json()

    future.funding_rate = future_dict["result"]["nextFundingRate"]

    return future
