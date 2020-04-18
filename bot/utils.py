import pytz
import urllib.request

from datetime import datetime

from constants import default_timezone


def embed_prices(data, key, embed, reverse):
    i = 0
    for d in sorted(data, key=lambda x: x["prices"][key], reverse=reverse):
        i += 1
        embed.add_field(
            name=d["username"] if i > 1 else ("Highest" if reverse else "Lowest"),
            value=d["prices"][key]
            if i > 1
            else str("""```py\n{} - {}```""".format(d["username"], d["prices"][key])),
            inline=True if i > 1 else False,
        )
    return embed


def format_insert_price(username: str, day: str, price: int, period: str):
    key = day + "-" + period if day != "Sun" else day
    return {"prices.{}".format(key): price, "username": username}


def format_remove_price(day: str, period: str):
    key = day + "-" + period if day != "Sun" else day
    return {"prices.{}".format(key): ""}


def get_user_date(data):
    tz = (
        pytz.timezone(data["timezone"])
        if data and "timezone" in data.keys()
        else pytz.timezone(default_timezone)
    )
    date = datetime.now(tz)
    return date


def tiny_url(url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urllib.request.urlopen(apiurl + url).read()
    return tinyurl.decode("utf-8")
