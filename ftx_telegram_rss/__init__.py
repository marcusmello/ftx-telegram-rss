__version__ = "0.1.1-alpha.0"

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
    __slots__ = [
        "_funding_rate_key",
        "_listed_futures_endpoint",
        "_future_detail_endpoint",
        "_output_number",
        "_output_treshold",
        "_futures_names",
    ]

    def __init__(self):
        self._funding_rate_key = "nextFundingRate"
        self._listed_futures_endpoint = "https://ftx.com/api/futures"
        self._future_detail_endpoint = "https://ftx.com/api/futures/{}/stats"
        self._output_number = env.int("OUTPUT_NUMBER")
        self._output_treshold = env.float("OUTPUT_THRESHOLD")
        self._get_futures_names()

    def _get_futures_names(self):
        """The sanitization of the list of names is dispensed here, Since
        this should be a simple script that solves an exercise. The user
        is expected to list existing FTX futures names; otherwise,
        nonexistent names will be ignored, due to the "try/catch" in
        '_unsorted_filtered_funding_rate_list'. So, as long as there is
        a few correct names in the list, it will run smoothly.
        """

        _input_list = env.list("LIST_OF_FUTURES")

        self._futures_names = (
            self.get_all_listed_futures_names()
            if _input_list == ["all"]
            else _input_list
        )

    def get_all_listed_futures_names(self) -> list:
        futures = (get_response(self._listed_futures_endpoint)).json()
        return [future["name"] for future in futures["result"]]

    def _unsorted_filtered_funding_rate_list(self) -> list:
        funding_rate_list = []

        for name in self._futures_names:
            try:
                future_dict = (
                    get_response(self._future_detail_endpoint.format(name))
                ).json()

                funding_rate = float(
                    future_dict["result"][self._funding_rate_key]
                )

                if funding_rate >= self._output_treshold:
                    funding_rate_list.append((name, funding_rate))

            except:  # The notable exception here is a nonexistent
                pass  # 'nextFundingRate' key in 'future_dict["result"]'

        return funding_rate_list

    def funding_rate_top_bottom_rich_list(self) -> RichList:
        rich_list = RichList()

        raw_list = self._unsorted_filtered_funding_rate_list()
        _list = sorted(raw_list, key=lambda future: future[1], reverse=True)

        n_top = n_bottom = self._output_number
        if len(_list) < self._output_number:
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
        self._process_time_seconds = 0
        self.msg = None
        self.futures = Futures()

        try:
            self.telegram_report = TelegramReport(
                token=env.str("TELEGRAM_TOKEN"),
                chat_id=env.int("TELEGRAM_CHAT_ID"),
            )
        except:
            self.telegram_report = None

    def _sleep(self):
        _sleep_time = (
            env.int("UPDATE_DELAY") - self._process_time_seconds
            if env.int("UPDATE_DELAY") > self._process_time_seconds
            else env.int("UPDATE_DELAY")
        )
        time.sleep(_sleep_time)

    def do_report(self, msg):
        print(msg)
        if self.telegram_report:
            self.telegram_report.send(msg)

    def run(self):
        while True:
            start_time = pendulum.now()
            futures_funding_rate_list = (
                self.futures.funding_rate_top_bottom_rich_list()
            )
            self.do_report(futures_funding_rate_list.as_formatted_text())
            self._process_time_seconds = (pendulum.now() - start_time).seconds
            self._sleep()
