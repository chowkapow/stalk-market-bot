import urllib.request
import pytz


from datetime import datetime

from constants import default_timezone


def tiny_url(url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urllib.request.urlopen(apiurl + url).read()
    return tinyurl.decode("utf-8")


def format_day(op: str, sell_time=""):
    if op == "buy":
        return "Sun"
    else:
        date = datetime.now()
        day = date.strftime("%a")
        sell_time = date.strftime("%p") if sell_time == "" else sell_time.upper()
        return day + "-" + sell_time


def format_insert_price(username: str, day: str, price: int, sell_time: str):
    key = day + "-" + sell_time if day != "Sun" else day
    return {"prices.{}".format(key): price, "username": username}


def format_remove_price(op: str, sell_time=""):
    key = format_day(op, sell_time)
    return {"prices.{}".format(key): ""}


def get_user_timezone(data):
    tz = (
        pytz.timezone(data["timezone"])
        if data and "timezone" in data.keys()
        else pytz.timezone(default_timezone)
    )
    return tz
