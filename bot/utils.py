import json
import urllib.request

from datetime import datetime


def is_turnip_trader():
    async def predicate(ctx):
        return "Turnip Trader" in [r.name for r in ctx.author.roles]

    return commands.check(predicate)


def read_json(filename):
    with open(filename) as readfile:
        data = json.load(readfile)
        return data


def tiny_url(url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urllib.request.urlopen(apiurl + url).read()
    return tinyurl.decode("utf-8")


def write_json(name, op, price, sell_time, env):
    date = datetime.now()
    filename = env + "_data.json"
    data = read_json(filename)
    if name not in data.keys():
        data[name] = {}
    if op == "buy":
        key = "Sun"
    else:
        day = date.strftime("%a")
        sell_time = date.strftime("%p") if sell_time == "" else sell_time.upper()
        key = day + "-" + sell_time
    data[name][key] = price
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=2)


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
