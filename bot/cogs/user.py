import discord

from datetime import datetime, timedelta
from discord.ext import commands
from operator import itemgetter

from constants import (
    error_messages as em,
    faq_message,
    help_command as hc,
    weekday_order,
)
from db import (
    get_user_by_id,
    get_user_by_username,
    get_users,
    upsert_user_data,
    remove_user_data,
)
from utils import (
    embed_prices,
    format_insert_price,
    format_insert_server,
    get_user_date,
    tiny_url,
)


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
            name=hc.get("faq_name"), value=hc.get("faq_value"), inline=False
        )
        embed.add_field(
            name=hc.get("add_name"), value=hc.get("add_value"), inline=False
        )
        embed.add_field(
            name=hc.get("today_name"), value=hc.get("today_value"), inline=False
        )
        # embed.add_field(
        #     name=hc.get("clear_name"), value=hc.get("clear_value"), inline=False
        # )
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
            name=hc.get("info_name"), value=hc.get("info_value"), inline=False
        )
        embed.add_field(
            name=hc.get("island_name"), value=hc.get("island_value"), inline=False
        )
        embed.add_field(name=hc.get("fc_name"), value=hc.get("fc_value"), inline=False)
        embed.add_field(
            name=hc.get("dodo_name"), value=hc.get("dodo_value"), inline=False
        )
        embed.set_footer(text=hc.get("footer"))
        await ctx.send(embed=embed)

    @commands.command()
    async def faq(self, ctx):
        embed = discord.Embed(title="FAQ", color=discord.Colour.dark_blue())
        for key, val in faq_message.items():
            embed.add_field(name=key, value=val, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def today(self, ctx):
        # Use default timezone
        date = get_user_date({})
        day = date.strftime("%a")
        period = date.strftime("%p")
        if day == "Sun":
            key = day
            buy_data = get_users(
                {
                    "prices.{}".format(key): {"$exists": True},
                    "servers": ctx.message.guild.id,
                },
                {"username": 1, "prices.{}".format(key): ""},
            )
            if buy_data:
                embed = discord.Embed(
                    title="Buy Prices", color=discord.Colour.dark_blue()
                )
                embed = embed_prices(buy_data, key, embed, False)
                embed.set_footer(text=date.strftime("%B %d, %I:%M %p %Z"))
                await ctx.send(embed=embed)
            else:
                await ctx.send(em["empty_buy"])
        else:
            embed = discord.Embed(title="Sell Prices", color=discord.Colour.dark_blue())
            if period == "AM":
                yesterday = (date - timedelta(days=1)).strftime("%a")
                key = yesterday + "-PM"
                yesterday_data = get_users(
                    {
                        "prices.{}".format(key): {"$exists": True},
                        "servers": ctx.message.guild.id,
                    },
                    {"username": 1, "prices.{}".format(key): ""},
                )
                if yesterday_data:
                    embed.add_field(
                        name="\u200b",
                        value="Yesterday's Afternoon Prices",
                        inline=False,
                    )
                    embed = embed_prices(yesterday_data, key, embed, True)
                key = day + "-" + period
                morning_data = get_users(
                    {
                        "prices.{}".format(key): {"$exists": True},
                        "servers": ctx.message.guild.id,
                    },
                    {"username": 1, "prices.{}".format(key): ""},
                )
                if morning_data:
                    embed.add_field(
                        name="\u200b", value="Today's Morning Prices", inline=False
                    )
                    embed = embed_prices(morning_data, key, embed, True)
                if yesterday_data or morning_data:
                    embed.set_footer(text=date.strftime("%B %d, %I:%M %p %Z"))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(em["empty_sell"])
            elif period == "PM":
                key = day + "-AM"
                morning_data = get_users(
                    {
                        "prices.{}".format(key): {"$exists": True},
                        "servers": ctx.message.guild.id,
                    },
                    {"username": 1, "prices.{}".format(key): ""},
                )
                if morning_data:
                    embed.add_field(
                        name="\u200b", value="Today's Morning Prices", inline=False
                    )
                    embed = embed_prices(morning_data, key, embed, True)
                key = day + "-" + period
                afternoon_data = get_users(
                    {
                        "prices.{}".format(key): {"$exists": True},
                        "servers": ctx.message.guild.id,
                    },
                    {"username": 1, "prices.{}".format(key): ""},
                )
                if afternoon_data:
                    embed.add_field(
                        name="\u200b", value="Today's Afternoon Prices", inline=False
                    )
                    embed = embed_prices(afternoon_data, key, embed, True)
                if morning_data or afternoon_data:
                    embed.set_footer(text=date.strftime("%B %d, %I:%M %p %Z"))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(em["empty_sell"])

    @commands.command()
    async def add(self, ctx, price: int, period=""):
        if price < 0 or (period != "" and period != "am" and period != "pm"):
            await ctx.send(em.get("invalid_input"))
        else:
            name = ctx.author.name
            user_data = get_user_by_id(ctx.author.id)
            date = get_user_date(user_data)
            day = date.strftime("%a")
            period = date.strftime("%p") if period == "" else period.upper()
            set = format_insert_price(name, day, price, period)
            addToSet = format_insert_server(ctx.message.guild.id)
            if upsert_user_data(ctx.author.id, set, addToSet):
                await ctx.send("Added {}'s price of {}.".format(name, price))
                await self.today(ctx)

    # @commands.command(name="clear")
    # async def clearPrices(self, ctx, op: str, sell_time=""):
    #     if (op != "" and op != "buy" and op != "sell") or (
    #         sell_time != "" and sell_time != "am" and sell_time != "pm"
    #     ):
    #         await ctx.send(em.get("invalid_input"))
    #     else:
    #         name = ctx.author.name
    #         user_data = get_user(ctx.author.id)
    #         tz = get_user_timezone(user_data)
    #         date = datetime.now(tz)
    #         data = format_remove_price(op, sell_time)
    #         remove_user_data(ctx.author.id, data)
    #         if op == "buy":
    #             self.bot._buy_prices.pop(ctx.author.name, None)
    #             await ctx.send("Cleared {}'s buy price.".format(name))
    #         else:
    #             if sell_time == "am":
    #                 self.bot._sell_morning_prices.pop(name, None)
    #                 await ctx.send("Cleared {}'s sell morning price.".format(name))
    #             elif sell_time == "pm":
    #                 self.bot._sell_afternoon_prices.pop(name, None)
    #                 await ctx.send("Cleared {}'s sell afternoon price.".format(name))
    #             else:
    #                 other_sell_time = "am" if date.strftime("%p") == "PM" else "pm"
    #                 remove_user_data(
    #                     ctx.author.id, format_remove_price(op, other_sell_time)
    #                 )
    #                 self.bot._sell_morning_prices.pop(name, None)
    #                 self.bot._sell_afternoon_prices.pop(name, None)
    #                 await ctx.send("Cleared {}'s sell prices.".format(name))

    @commands.command()
    async def history(self, ctx):
        user_data = get_user_by_id(ctx.author.id)
        if "prices" in user_data.keys() and len(user_data["prices"]) > 0:
            date = get_user_date(user_data)
            user = ctx.author.name
            embed = discord.Embed(
                title=user + "'s Prices", color=discord.Colour.dark_blue()
            )
            for key, val in sorted(
                user_data["prices"].items(), key=lambda x: weekday_order[x[0]]
            ):
                embed.add_field(name=key, value=val, inline=False)
            embed.set_footer(text=date.strftime("%B %d, %I:%M %p %Z"))
            await ctx.send(embed=embed)
        else:
            await ctx.send(em.get("no_data"))

    @commands.command()
    async def trends(self, ctx):
        user_data = get_user_by_id(ctx.author.id)
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
        set = {"timezone": tz, "username": ctx.author.name}
        addToSet = format_insert_server(ctx.message.guild.id)
        upsert_user_data(ctx.author.id, set, addToSet)
        await ctx.send("{}'s timezone updated to {}".format(ctx.author.name, tz))

    @commands.command()
    async def info(self, ctx, username=""):
        if username == "":
            user_data = get_user_by_id(ctx.author.id)
        else:
            user_data = get_user_by_username(username, ctx.message.guild.id)
        if user_data and (
            "fc" in user_data.keys()
            or "island" in user_data.keys()
            or "dodo" in user_data.keys()
        ):
            embed = discord.Embed(
                title=user_data["username"] + "'s Info",
                color=discord.Colour.dark_blue(),
            )
            if "fc" in user_data.keys():
                embed.add_field(name="Friend Code", value=user_data["fc"], inline=False)
            if "island" in user_data.keys():
                embed.add_field(name="Island", value=user_data["island"], inline=False)
            if "dodo" in user_data.keys():
                embed.add_field(name="Dodo Code", value=user_data["dodo"], inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(em.get("no_data"))

    @commands.command()
    async def island(self, ctx, name: str):
        set = {"island": name, "username": ctx.author.name}
        addToSet = format_insert_server(ctx.message.guild.id)
        upsert_user_data(ctx.author.id, set, addToSet)
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
            set = {"fc": friend_code, "username": ctx.author.name}
            addToSet = format_insert_server(ctx.message.guild.id)
            upsert_user_data(ctx.author.id, set, addToSet)
            await ctx.send(
                "{}'s friend code updated to {}".format(ctx.author.name, friend_code)
            )
        else:
            await ctx.send(em.get("invalid_input"))

    @commands.command()
    async def dodo(self, ctx, dodo_code: str):
        if dodo_code.lower() == "clear" and remove_user_data(
            ctx.author.id, {"dodo": ""}
        ):
            await ctx.send("Cleared {}'s dodo code".format(ctx.author.name))
        elif len(dodo_code) == 5:
            set = {"dodo": dodo_code, "username": ctx.author.name}
            addToSet = format_insert_server(ctx.message.guild.id)
            upsert_user_data(ctx.author.id, set, addToSet)
            await ctx.send(
                "{}'s dodo code updated to {}".format(ctx.author.name, dodo_code)
            )
        else:
            await ctx.send(em.get("invalid_input"))


def setup(bot):
    bot.add_cog(User(bot))
