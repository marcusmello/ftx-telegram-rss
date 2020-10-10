__version__ = "0.1.1-alpha.1"

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


def fancy_datetime(_dt) -> str:
    _date = _dt.to_formatted_date_string()
    _time = "{}00:00".format(_dt.to_time_string()[:-5])
    return "[{} - {}]".format(_date, _time)


def display_futures(_list: list) -> str:
    return "".join(
        ["{} ({})\n".format(future[0], future[1]) for future in _list]
    )


class RichList:
    top = []
    bottom = []

    def as_list(self) -> list:
        return self.top + self.bottom

    def as_formatted_text(self) -> str:
        msg_template = """{}\n\nTop {}:\n\n{}\n\nBottom {}:\n\n{}"""

        return msg_template.format(
            fancy_datetime(pendulum.now("UTC")),
            len(self.top),
            display_futures(self.top),
            len(self.bottom),
            display_futures(self.bottom),
        )


class Futures:
    __slots__ = [
        "_list_all_futures_endpoint",
        "_future_funding_rates_endpoint",
        "_output_number",
        "_output_treshold",
        "_futures_names",
    ]

    def __init__(self):
        self._list_all_futures_endpoint = "https://ftx.com/api/futures"
        self._future_funding_rates_endpoint = (
            "https://ftx.com/api/funding_rates"
        )
        self._output_number = env.int("OUTPUT_NUMBER")
        self._output_treshold = env.float("OUTPUT_THRESHOLD")
        self._get_futures_names()

    def _get_futures_names(self):
        """The sanitization of the list of names is dispensed here, Since
        this should be a simple script that solves an exercise. The user
        is expected to list existing FTX futures names; otherwise,
        nonexistent names will be ignored. So, as long as there is
        a few correct names in the list, it will run smoothly.
        """

        _input_list = env.list("LIST_OF_FUTURES")

        self._futures_names = (
            self.get_all_listed_futures_names()
            if _input_list == ["all"]
            else _input_list
        )

    def get_all_listed_futures_names(self) -> list:
        futures = (get_response(self._list_all_futures_endpoint)).json()
        return [future["name"] for future in futures["result"]]

    def _unsorted_filtered_funding_rate_list(self) -> list:
        futures_and_funding_rate_tuple_list = []
        utc_now = pendulum.now("UTC")
        fmt = "YYYY-MM-DDTHH:mm:ssZZ"

        _info = (get_response(self._future_funding_rates_endpoint)).json()
        for result in _info["result"]:
            try:
                future = result["future"]
                rate = result["rate"]
                _time = pendulum.from_format(result["time"], fmt)
                delay = (utc_now - _time).as_interval()

                if (
                    delay.hours < 1
                    and rate > self._output_treshold
                    and future in self._futures_names
                ):
                    futures_and_funding_rate_tuple_list.append((future, rate))
            except:
                pass

        return futures_and_funding_rate_tuple_list

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
