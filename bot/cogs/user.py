import discord
import pytz

import constants

from datetime import datetime, timedelta
from discord.ext import commands
from operator import itemgetter

from constants import (
    error_messages as em,
    help_command as hc,
    weekday_order,
)
from db import get_user, upsert_user_data, remove_user_data, remove_all_data
from utils import format_insert_price, format_remove_price, get_user_timezone, tiny_url


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title=hc.get("title"),
            description=hc.get("description"),
            color=discord.Colour.dark_blue(),
        )
        embed.add_field(
            name=hc.get("help_name"), value=hc.get("help_value"), inline=False
        )
        embed.add_field(
            name=hc.get("buy_name"), value=hc.get("buy_value"), inline=False
        )
        embed.add_field(
            name=hc.get("sell_name"), value=hc.get("sell_value"), inline=False
        )
        embed.add_field(
            name=hc.get("add_name"), value=hc.get("add_value"), inline=False
        )
        embed.add_field(
            name=hc.get("clear_name"), value=hc.get("clear_value"), inline=False
        )
        embed.add_field(
            name=hc.get("history_name"), value=hc.get("history_value"), inline=False
        )
        embed.add_field(
            name=hc.get("trends_name"), value=hc.get("trends_value"), inline=False
        )
        embed.add_field(
            name=hc.get("timezone_name"), value=hc.get("timezone_value"), inline=False
        )
        embed.add_field(
            name=hc.get("island_name"), value=hc.get("island_value"), inline=False
        )
        embed.add_field(name=hc.get("fc_name"), value=hc.get("fc_value"), inline=False)
        embed.set_footer(text=hc.get("footer"))
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx):
        if len(self.bot._buy_prices) == 0:
            await ctx.send(em.get("empty_buy"))
        else:
            user_data = get_user(ctx.author.id)
            tz = get_user_timezone(user_data)
            date = datetime.now(tz).strftime("%B %d, %I:%M %p %Z")
            embed = discord.Embed(title="Buy Prices", color=discord.Colour.dark_blue())
            i = 0
            for key, val in sorted(self.bot._buy_prices.items(), key=lambda x: x[1]):
                i += 1
                embed.add_field(
                    name=key if i > 1 else "Lowest",
                    value=val
                    if i > 1
                    else str("""```py\n{0} - {1}```""".format(key, val)),
                    inline=True if i > 1 else False,
                )
            embed.set_footer(text=date)
            await ctx.send(embed=embed)

    @commands.command()
    async def sell(self, ctx):
        if (
            len(self.bot._sell_morning_prices) == 0
            and len(self.bot._sell_afternoon_prices) == 0
        ):
            await ctx.send(em.get("empty_sell"))
        else:
            user_data = get_user(ctx.author.id)
            tz = get_user_timezone(user_data)
            date = datetime.now(tz).strftime("%B %d, %I:%M %p %Z")
            embed = discord.Embed(title="Sell Prices", color=discord.Colour.dark_blue())
            if len(self.bot._sell_morning_prices) > 0:
                embed.add_field(
                    name="\u200b", value="Sell Morning Prices", inline=False
                )
                i = 0
                for key, val in sorted(
                    self.bot._sell_morning_prices.items(),
                    key=lambda x: x[1],
                    reverse=True,
                ):
                    i += 1
                    embed.add_field(
                        name=key if i > 1 else "Highest",
                        value=val
                        if i > 1
                        else str("""```py\n{0} - {1}```""".format(key, val)),
                        inline=True if i > 1 else False,
                    )
            if len(self.bot._sell_afternoon_prices) > 0:
                embed.add_field(
                    name="\u200b", value="Sell Afternoon Prices", inline=False
                )
                i = 0
                for key, val in sorted(
                    self.bot._sell_afternoon_prices.items(),
                    key=lambda x: x[1],
                    reverse=True,
                ):
                    i += 1
                    embed.add_field(
                        name=key if i > 1 else "Highest",
                        value=val
                        if i > 1
                        else str("""```py\n{0} - {1}```""".format(key, val)),
                        inline=True if i > 1 else False,
                    )
            embed.set_footer(text=date)
            await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, op: str, price: int, sell_time=""):
        if (
            (op != "buy" and op != "sell")
            or price < 0
            or (sell_time != "" and sell_time != "am" and sell_time != "pm")
        ):
            await ctx.send(em.get("invalid_input"))
        else:
            name = ctx.author.name
            user_data = get_user(ctx.author.id)
            tz = get_user_timezone(user_data)
            date = datetime.now(tz)
            if sell_time == "":
                sell_time = date.strftime("%p").lower()
            data = format_insert_price(name, op, price, sell_time)
            if upsert_user_data(ctx.author.id, data):
                await ctx.send("Added {0}'s {1} price of {2}.".format(name, op, price))
            if op == "buy":
                self.bot._buy_prices[name] = price
                await self.buy(ctx)
            else:
                if (date.hour < 12 and sell_time == "") or sell_time == "am":
                    self.bot._sell_morning_prices[name] = price
                elif (date.hour >= 12 and sell_time == "") or sell_time == "pm":
                    self.bot._sell_afternoon_prices[name] = price
                await self.sell(ctx)

    @commands.command(name="clear")
    async def clearPrices(self, ctx, op: str, sell_time=""):
        if (op != "" and op != "buy" and op != "sell") or (
            sell_time != "" and sell_time != "am" and sell_time != "pm"
        ):
            await ctx.send(em.get("invalid_input"))
        else:
            name = ctx.author.name
            user_data = get_user(ctx.author.id)
            tz = get_user_timezone(user_data)
            date = datetime.now(tz)
            data = format_remove_price(op, sell_time)
            remove_user_data(ctx.author.id, data)
            if op == "buy":
                self.bot._buy_prices.pop(ctx.author.name, None)
                await ctx.send("Cleared {0}'s buy price.".format(name))
            else:
                if sell_time == "am":
                    self.bot._sell_morning_prices.pop(name, None)
                    await ctx.send("Cleared {0}'s sell morning price.".format(name))
                elif sell_time == "pm":
                    self.bot._sell_afternoon_prices.pop(name, None)
                    await ctx.send("Cleared {0}'s sell afternoon price.".format(name))
                else:
                    other_sell_time = "am" if date.strftime("%p") == "PM" else "pm"
                    remove_user_data(
                        ctx.author.id, format_remove_price(op, other_sell_time)
                    )
                    self.bot._sell_morning_prices.pop(name, None)
                    self.bot._sell_afternoon_prices.pop(name, None)
                    await ctx.send("Cleared {0}'s sell prices.".format(name))

    @commands.command()
    async def history(self, ctx):
        user_data = get_user(ctx.author.id)
        if "prices" in user_data.keys() and len(user_data["prices"]) > 0:
            tz = get_user_timezone(user_data)
            date = datetime.now(tz).strftime("%B %d, %I:%M %p %Z")
            user = ctx.author.name
            embed = discord.Embed(
                title=user + "'s Prices", color=discord.Colour.dark_blue()
            )
            for key, val in sorted(
                user_data["prices"].items(), key=lambda x: weekday_order[x[0]]
            ):
                embed.add_field(name=key, value=val, inline=False)
            embed.set_footer(text=date)
            await ctx.send(embed=embed)
        else:
            await ctx.send(em.get("no_data"))

    @commands.command()
    async def trends(self, ctx):
        user_data = get_user(ctx.author.id)
        if "prices" in user_data.keys() and len(user_data["prices"]) > 0:
            prices = ""
            missing_days = set(weekday_order.keys()) - set(user_data["prices"].keys())
            for d in missing_days:
                user_data["prices"][d] = ""
            for key, val in sorted(
                user_data["prices"].items(), key=lambda x: weekday_order[x[0]]
            ):
                prices += str(val) + "."
            url = "https://turnipprophet.io/index.html?prices={}".format(prices)
            await ctx.send(
                "{}'s trends here: {}".format(ctx.author.name, tiny_url(url))
            )
        else:
            await ctx.send(em.get("no_data"))

    @commands.command()
    async def timezone(self, ctx, tz: str):
        data = {"timezone": tz}
        upsert_user_data(ctx.author.id, data)
        await ctx.send("{}'s timezone updated to {}".format(ctx.author.name, tz))

    @commands.command()
    async def island(self, ctx, name: str):
        data = {"island": name}
        upsert_user_data(ctx.author.id, data)
        await ctx.send("{}'s island updated to {}".format(ctx.author.name, name))

    @commands.command()
    async def fc(self, ctx, friend_code: str):
        dashes = itemgetter(2, 7, 12)(friend_code)
        if (
            len(friend_code) == 17
            and friend_code[0:2] == "SW"
            and all(d == dashes[0] for d in dashes)
            and dashes[0] == "-"
            and friend_code[3:7].isdigit()
            and friend_code[8:12].isdigit()
            and friend_code[13:17].isdigit()
        ):
            data = {"fc": friend_code}
            upsert_user_data(ctx.author.id, data)
            await ctx.send(
                "{}'s friend code updated to {}".format(ctx.author.name, friend_code)
            )
        else:
            await ctx.send(em.get("invalid_input"))


def setup(bot):
    bot.add_cog(User(bot))
