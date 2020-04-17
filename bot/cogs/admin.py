import discord

from datetime import datetime
from discord.ext import commands

from db import get_user, get_users, upsert_user_data, remove_user_data
from .user import User as user
from utils import format_insert_price, format_remove_price, get_user_timezone


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def admin_add(self, ctx, name: str, id: int, price: int, sell_time=""):
        user_data = get_user(id)
        tz = get_user_timezone(user_data)
        date = datetime.now(tz)
        day = date.strftime("%a")
        if sell_time == "":
            sell_time = date.strftime("%p").lower()
        data = format_insert_price(name, day, price, sell_time.upper())
        if upsert_user_data(id, data):
            await ctx.send("Added {}'s price of {}.".format(name, price))
        if day == "Sun":
            self.bot._buy_prices[name] = price
            await user.buy(self, ctx)
        else:
            if (date.hour < 12 and sell_time == "") or sell_time == "am":
                self.bot._sell_morning_prices[name] = price
            elif (date.hour >= 12 and sell_time == "") or sell_time == "pm":
                self.bot._sell_afternoon_prices[name] = price
            await user.sell(self, ctx)

    @commands.command()
    @commands.is_owner()
    async def admin_clear(self, ctx, name: str, id: int, op: str, sell_time=""):
        sell_time = sell_time.lower()
        data = format_remove_price(op, sell_time)
        remove_user_data(id, data)
        if op == "buy":
            self.bot._buy_prices.pop(name, None)
            await ctx.send("Cleared {}'s buy price.".format(name))
        else:
            if sell_time == "am":
                self.bot._sell_morning_prices.pop(name, None)
                await ctx.send("Cleared {}'s sell morning price.".format(name))
            elif sell_time == "pm":
                self.bot._sell_afternoon_prices.pop(name, None)
                await ctx.send("Cleared {}'s sell afternoon price.".format(name))
            else:
                other_sell_time = (
                    "am" if datetime.now().strftime("%p") == "PM" else "pm"
                )
                remove_user_data(id, format_remove_price(op, other_sell_time))
                self.bot._sell_morning_prices.pop(name, None)
                self.bot._sell_afternoon_prices.pop(name, None)
                await ctx.send("Cleared {}'s sell prices.".format(name))

    @commands.command()
    @commands.is_owner()
    async def admin_restore(self, ctx):
        data = get_users()
        date = datetime.now()
        today = date.strftime("%a")
        for i in data:
            if today == "Sun" and today in i["prices"].keys():
                self.bot._buy_prices[i["username"]] = i["prices"][today]
            else:
                if (today + "-AM") in i["prices"].keys():
                    self.bot._sell_morning_prices[i["username"]] = i["prices"][
                        today + "-AM"
                    ]
                if (today + "-PM") in i["prices"].keys():
                    self.bot._sell_afternoon_prices[i["username"]] = i["prices"][
                        today + "-PM"
                    ]

        if (
            len(self.bot._buy_prices) > 0
            or len(self.bot._sell_morning_prices) > 0
            or len(self.bot._sell_afternoon_prices) > 0
        ):
            await ctx.send("Restore complete.")
        else:
            await ctx.send("No data to restore.")

    # @bot.event
    # async def on_command_error(ctx, error):
    #     await ctx.send("Invalid input - please try again.")


def setup(bot):
    bot.add_cog(Admin(bot))
