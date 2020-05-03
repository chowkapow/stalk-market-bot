import discord
import pytz

from datetime import datetime, timedelta
from discord.ext import commands
from operator import itemgetter

from constants import (
    bells,
    error_messages as em,
    faq_message,
    help_command as hc,
    patterns,
    patterns_names,
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
            name=hc.get("pattern_name"), value=hc.get("pattern_value"), inline=False
        )
        embed.add_field(
            name=hc.get("info_name"), value=hc.get("info_value"), inline=False
        )
        embed.add_field(
            name=hc.get("dodo_name"), value=hc.get("dodo_value"), inline=False
        )
        embed.add_field(
            name=hc.get("bells_name"), value=hc.get("bells_value"), inline=False
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
                await ctx.send(em.get("empty_buy"))
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
                    await ctx.send(em.get("empty_sell"))
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
                    await ctx.send(em.get("empty_sell"))

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
                await self.trends(ctx)

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
            if "pattern" in user_data.keys():
                embed.add_field(
                    name="Last week's pattern",
                    value=patterns_names[user_data["pattern"]],
                    inline=False,
                )
            if "nextPattern" in user_data.keys():
                embed.add_field(
                    name="This week's pattern",
                    value=patterns_names[user_data["nextPattern"]],
                    inline=False,
                )
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
            if "pattern" in user_data.keys():
                url += "&pattern=" + str(patterns[user_data["pattern"]])
            await ctx.send(
                "{}'s trends here: {}".format(ctx.author.name, tiny_url(url))
            )
        else:
            await ctx.send(em.get("no_data"))

    @commands.command()
    async def pattern(self, ctx, pattern: str, next=""):
        pattern = pattern.lower()
        if pattern in patterns.keys():
            if next == "":
                set = {"pattern": pattern, "username": ctx.author.name}
                msg = ""
            else:
                set = {"nextPattern": pattern, "username": ctx.author.name}
                msg = "for next week "
            addToSet = format_insert_server(ctx.message.guild.id)
            if upsert_user_data(ctx.author.id, set, addToSet):
                await ctx.send(
                    "{}'s pattern {}updated to {}".format(
                        ctx.author.name, msg, patterns_names[pattern]
                    )
                )
        else:
            await ctx.send(em.get("invalid_input"))

    @commands.command()
    async def timezone(self, ctx, tz: str):
        if tz in pytz.all_timezones:
            set = {"timezone": tz, "username": ctx.author.name}
            addToSet = format_insert_server(ctx.message.guild.id)
            upsert_user_data(ctx.author.id, set, addToSet)
            await ctx.send("{}'s timezone updated to {}".format(ctx.author.name, tz))
        else:
            await ctx.send(em.get("invalid_input"))

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
    async def island(self, ctx, name=""):
        if name == "":
            user_data = get_user_by_id(ctx.author.id)
            if user_data and "island" in user_data.keys():
                await ctx.send(
                    "{}'s island: {}".format(ctx.author.name, user_data["island"])
                )
            else:
                await ctx.send(em.get("no_data"))
        else:
            set = {"island": name, "username": ctx.author.name}
            addToSet = format_insert_server(ctx.message.guild.id)
            upsert_user_data(ctx.author.id, set, addToSet)
            await ctx.send("{}'s island updated to {}".format(ctx.author.name, name))

    @commands.command()
    async def fc(self, ctx, friend_code=""):
        if friend_code == "":
            user_data = get_user_by_id(ctx.author.id)
            if user_data and "fc" in user_data.keys():
                await ctx.send("{}'s fc: {}".format(ctx.author.name, user_data["fc"]))
            else:
                await ctx.send(em.get("no_data"))
        else:
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
                    "{}'s friend code updated to {}".format(
                        ctx.author.name, friend_code
                    )
                )
            else:
                await ctx.send(em.get("invalid_input"))

    @commands.command()
    async def dodo(self, ctx, dodo_code=""):
        if dodo_code == "":
            user_data = get_user_by_id(ctx.author.id)
            if user_data and "dodo" in user_data.keys():
                await ctx.send(
                    "{}'s dodo code: {}".format(ctx.author.name, user_data["dodo"])
                )
            else:
                await ctx.send(em.get("no_data"))
        elif dodo_code.lower() == "clear" and remove_user_data(
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

    @commands.command()
    async def bells(self, ctx):
        await ctx.send(bells)


def setup(bot):
    bot.add_cog(User(bot))
