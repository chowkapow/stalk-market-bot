import discord

from datetime import datetime, timedelta
from discord.ext import commands

from .user import User as user
from utils import read_json, write_json


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    # @is_turnip_trader()
    async def admin_add(self, ctx, name: str, op: str, price: int, selltime=""):
        selltime = selltime.lower()
        await ctx.send("Added {0}'s {1} price of {2}.".format(name, op, price))
        write_json(name, op, price, selltime, self.bot._env)
        if op == "buy":
            self.bot._buy_prices[name] = price
            await user.buy(self, ctx)
        else:
            if (datetime.now().hour < 12 and selltime == "") or selltime == "am":
                self.bot._sell_morning_prices[name] = price
            elif (datetime.now().hour >= 12 and selltime == "") or selltime == "pm":
                self.bot._sell_afternoon_prices[name] = price
            await user.sell(self, ctx)

    @commands.command()
    @commands.is_owner()
    # @is_turnip_trader()
    async def admin_clear(self, ctx, name="", op="", selltime=""):
        selltime = selltime.lower()
        if op == "buy":
            self.bot._buy_prices.pop(name, None)
            await ctx.send("Cleared {0}'s buy price.".format(name))
        elif op == "sell":
            if selltime == "am":
                self.bot._sell_morning_prices.pop(name, None)
                await ctx.send("Cleared {0}'s sell morning price.".format(name))
            elif selltime == "pm":
                self.bot._sell_afternoon_prices.pop(name, None)
                await ctx.send("Cleared {0}'s sell afternoon price.".format(name))
            else:
                self.bot._sell_morning_prices.pop(name, None)
                self.bot._sell_afternoon_prices.pop(name, None)
                await ctx.send("Cleared {0}'s sell prices.".format(name))
        elif name != "":
            self.bot._buy_prices.pop(name, None)
            self.bot._sell_morning_prices.pop(name, None)
            self.bot._sell_afternoon_prices.pop(name, None)
            await ctx.send("Cleared {0}'s buy/sell prices.".format(name))
        else:
            self.bot._buy_prices.clear()
            self.bot._sell_morning_prices.clear()
            self.bot._sell_afternoon_prices.clear()
            await ctx.send("Cleared all prices.")

    @commands.command()
    @commands.is_owner()
    # @is_turnip_trader()
    async def admin_restore(self, ctx):
        date = datetime.now()
        data = read_json(self.bot._env + "_data.json")
        today = date.strftime("%a")
        for user, user_data in data.items():
            if today == "Sun":
                if today in user_data.keys():
                    self.bot._buy_prices[user] = user_data[today]
            else:
                if (today + "-AM") in user_data.keys():
                    self.bot._sell_morning_prices[user] = user_data[today + "-AM"]
                if (today + "-PM") in user_data.keys():
                    self.bot._sell_afternoon_prices[user] = user_data[today + "-PM"]
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
