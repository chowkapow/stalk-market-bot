import urllib.request

from datetime import datetime


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


def format_insert_price(nickname: str, op: str, price: int, sell_time=""):
    key = format_day(op, sell_time)
    return {"prices.{}".format(key): price, "nickname": nickname}


def format_remove_price(op: str, sell_time=""):
    key = format_day(op, sell_time)
    return {"prices.{}".format(key): ""}
