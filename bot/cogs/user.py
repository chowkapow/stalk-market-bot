import discord
import pytz

import constants

from datetime import datetime, timedelta
from discord.ext import commands

from constants import error_messages as em, help_command as hc, timezone, weekday_order
from utils import read_json, tiny_url, write_json


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
        embed.set_footer(text=hc.get("footer"))
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx):
        if len(self.bot._buy_prices) == 0:
            await ctx.send(em.get("empty_buy"))
        else:
            date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
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
            date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
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
    async def add(self, ctx, op: str, price: int, selltime=""):
        selltime = selltime.lower()
        if (
            (op != "buy" and op != "sell")
            or price < 0
            or (selltime != "" and selltime != "am" and selltime != "pm")
        ):
            await ctx.send(em.get("invalid_input"))
        else:
            await ctx.send(
                "Added {0}'s {1} price of {2}.".format(ctx.author.name, op, price)
            )
            write_json(ctx.author.name, op, price, selltime, self.bot._env)
            if op == "buy":
                self.bot._buy_prices[ctx.author.name] = price
                await self.buy(ctx)
            else:
                if (datetime.now().hour < 12 and selltime == "") or selltime == "am":
                    self.bot._sell_morning_prices[ctx.author.name] = price
                elif (datetime.now().hour >= 12 and selltime == "") or selltime == "pm":
                    self.bot._sell_afternoon_prices[ctx.author.name] = price
                await self.sell(ctx)

    @commands.command(name="clear")
    async def clearPrices(self, ctx, op="", selltime=""):
        selltime = selltime.lower()
        if (op != "" and op != "buy" and op != "sell") or (
            selltime != "" and selltime != "am" and selltime != "pm"
        ):
            await ctx.send(em.get("invalid_input"))
        else:
            if op == "buy":
                self.bot._buy_prices.pop(ctx.author.name, None)
                await ctx.send("Cleared {0}'s buy price.".format(ctx.author.name))
            elif op == "sell":
                if selltime == "am":
                    self.bot._sell_morning_prices.pop(ctx.author.name, None)
                    await ctx.send(
                        "Cleared {0}'s sell morning price.".format(ctx.author.name)
                    )
                elif selltime == "pm":
                    self.bot._sell_afternoon_prices.pop(ctx.author.name, None)
                    await ctx.send(
                        "Cleared {0}'s sell afternoon price.".format(ctx.author.name)
                    )
                else:
                    self.bot._sell_morning_prices.pop(ctx.author.name, None)
                    self.bot._sell_afternoon_prices.pop(ctx.author.name, None)
                    await ctx.send("Cleared {0}'s sell prices.".format(ctx.author.name))
            else:
                self.bot._buy_prices.pop(ctx.author.name, None)
                self.bot._sell_morning_prices.pop(ctx.author.name, None)
                self.bot._sell_afternoon_prices.pop(ctx.author.name, None)
                await ctx.send("Cleared {0}'s buy/sell prices.".format(ctx.author.name))

    @commands.command()
    async def history(self, ctx):
        data = read_json(self.bot._env + "_data.json")
        user = ctx.author.name
        if user in data.keys():
            date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
            embed = discord.Embed(
                title=user + "'s Prices", color=discord.Colour.dark_blue()
            )
            for key, val in sorted(
                data[user].items(), key=lambda x: weekday_order[x[0]]
            ):
                embed.add_field(name=key, value=val, inline=False)
            embed.set_footer(text=date)
            await ctx.send(embed=embed)
        else:
            await ctx.send(em.get("no_data"))

    @commands.command()
    async def trends(self, ctx):
        data = read_json(self.bot._env + "_data.json")
        user = ctx.author.name
        prices = ""
        if user in data.keys():
            missing_days = set(weekday_order.keys()) - set(data[user].keys())
            for d in missing_days:
                data[user][d] = ""
            for key, val in sorted(
                data[user].items(), key=lambda x: weekday_order[x[0]]
            ):
                prices += str(val) + "."
            url = "https://turnipprophet.io/index.html?prices={}".format(prices)
            await ctx.send(
                "{}'s trends here: {}".format(ctx.author.name, tiny_url(url))
            )
        else:
            await ctx.send(em.get("no_data"))


def setup(bot):
    bot.add_cog(User(bot))
