__version__ = "0.1.0"

import time
import pendulum
import requests
import telegram
from environs import Env

env = Env()
env.read_env()


def get_response(endpoint: str):
    with requests.get(endpoint) as response:
        if response.status_code == 200:
            return response


def display_futures(rich_list) -> str:
    return "".join(
        ["{} ({})\n".format(future[0], future[1]) for future in rich_list]
    )


class RichList:
    top = []
    bottom = []

    def as_list(self) -> list:
        return self.top + self.bottom

    def as_formatted_text(self) -> str:
        _now = pendulum.now().to_datetime_string()
        msg_template = """{}\n\nTop {}:\n\n{}\n\nBottom {}:\n\n{}"""

        return msg_template.format(
            _now,
            len(self.top),
            display_futures(self.top),
            len(self.bottom),
            display_futures(self.bottom),
        )


class Futures:
    def __init__(self):
        self._funding_rate_key = "nextFundingRate"
        self.listed_futures_endpoint = "https://ftx.com/api/futures"
        self.future_detail_endpoint = "https://ftx.com/api/futures/{}/stats"
        self.output_number = env.int("OUTPUT_NUMBER")
        self.output_treshold = env.float("OUTPUT_THRESHOLD")
        self._get_futures_names()

    def _get_futures_names(self):
        _input_list = env.list("LIST_OF_FUTURES")
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

            except:  # The notable exception here is a nonexistent
                pass  # 'nextFundingRate' key in 'future_dict["result"]'

        return funding_rate_list

    def funding_rate_list(self):
        rich_list = RichList()

        raw_list = self._original_funding_rate_list()
        _list = sorted(raw_list, key=lambda future: future[1], reverse=True)

        n_top = n_bottom = self.output_number
        if len(_list) < self.output_number:
            n_top = int(len(_list) / 2)
            n_bottom = len(_list) - n_top

        rich_list.top = _list[:n_top]
        rich_list.bottom = _list[-n_bottom:]

        return rich_list


class TelegramReport:
    def __init__(self, token, chat_id) -> None:
        self.chat_id = chat_id
        self.bot = telegram.Bot(token)

    def send(self, message):
        self.bot.send_message(chat_id=self.chat_id, text=message)


class CheckAndReport:
    def __init__(self) -> None:
        self.msg = None
        self.futures = Futures()

        try:
            self.telegram_report = TelegramReport(
                token=env.str("TELEGRAM_TOKEN"),
                chat_id=env.int("TELEGRAM_CHAT_ID"),
            )
        except:
            self.telegram_report = None

    def do_report(self, msg):
        print(msg)
        if self.telegram_report:
            self.telegram_report.send(msg)

    def run(self):
        while True:
            futures_funding_rate_list = self.futures.funding_rate_list()
            self.do_report(futures_funding_rate_list.as_formatted_text())
            time.sleep(env.int("UPDATE_DELAY"))


if __name__ == "__main__":
    check_and_report = CheckAndReport()
    check_and_report.run()
