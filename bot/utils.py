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


def write_json(name, op, price, selltime, env):
    date = datetime.now()
    filename = env + "_data.json"
    data = read_json(filename)
    if name not in data.keys():
        data[name] = {}
    if op == "buy":
        key = "Sun"
    else:
        day = date.strftime("%a")
        selltime = date.strftime("%p") if selltime == "" else selltime.upper()
        key = day + "-" + selltime
    data[name][key] = price
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=2)
