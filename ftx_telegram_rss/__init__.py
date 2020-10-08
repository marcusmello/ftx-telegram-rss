__version__ = "0.1.0"

import requests


def get_response(endpoint: str):
    with requests.get(endpoint) as response:
        if response.status_code == 200:
            return response


class Futures:
    def __init__(self):
        self.listed_futures_endpoint = "https://ftx.com/api/futures"
        self.future_detail_endpoint = "https://ftx.com/api/futures/{}/stats"
        self.OUTPUT_NUMBER = 3
        self._funding_rate_key = "nextFundingRate"
        self._futures_names = self.get_all_listed_futures_names()

    def get_all_listed_futures_names(self) -> list:
        futures = (get_response(self.listed_futures_endpoint)).json()

        return [future["name"] for future in futures["result"]]

    def _future(self, name):
        future_dict = (
            get_response(self.future_detail_endpoint.format(name))
        ).json()

        funding_rate = future_dict["result"][self._funding_rate_key]

        return (name, funding_rate)

    def _original_funding_rate_list(self):
        funding_rate_list = []

        for name in self._futures_names:
            try:
                funding_rate_list.append(self._future(name))

            except:  # Exception as e:
                pass
                # print(e)

        return funding_rate_list

    def funding_rate_list(self):
        _list = sorted(
            self._original_funding_rate_list(), key=lambda future: future[1]
        )[::-1]

        _top = _list[: self.OUTPUT_NUMBER]
        _bottom = _list[-self.OUTPUT_NUMBER :]

        return _top + _bottom
