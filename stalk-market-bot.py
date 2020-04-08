import asyncio
import discord
import logging
import os
import pytz
import sys

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv

env = 'dev' if len(sys.argv) == 1 else sys.argv[1]
# Change reset time here
reset_time = 3  # 3 AM

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename=env+'_discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
if env == 'dev':
    TOKEN = os.getenv('dev_DISCORD_TOKEN')
elif env == 'dcbc':
    TOKEN = os.getenv('dcbc_DISCORD_TOKEN')
else:
    TOKEN = os.getenv('leftovers_DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')

buy_prices = {}
sell_morning_prices = {}
sell_afternoon_prices = {}
timezone = pytz.timezone('America/Chicago')

# Bot commands
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title='Help Menu',
        description='I\'ll help you find the best prices for turnips!',
        color=discord.Colour.dark_blue())
    embed.add_field(name='**$help**', value="List commands", inline=False)
    embed.add_field(
        name='**$all**', value="List all buy/sell prices", inline=False)
    embed.add_field(name='**$buy**',
                    value="List buy prices only", inline=False)
    embed.add_field(name='**$sell**',
                    value="List sell prices only", inline=False)
    embed.add_field(
        name='**$add**', value="Add your price with \"$add buy n\", \"$add sell n\", \"$add sell n am\", \"$add sell n pm\"", inline=False)
    embed.add_field(
        name='**$clear**', value="Clear your prices with \"$clear\", \"$clear buy\", \"$clear sell\", \"$clear sell am\", \"$clear sell pm\"", inline=False)
    embed.set_footer(text="Feedback welcome. Contact chowkapow#4085")
    await ctx.send(embed=embed)


@bot.command()
async def all(ctx):
    if len(buy_prices) == 0 and len(sell_morning_prices) == 0 and len(sell_afternoon_prices) == 0:
        await ctx.send("No prices at this time.")
    else:
        date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
        embed = discord.Embed(
            title='All Prices',
            color=discord.Colour.dark_blue())
        if len(buy_prices) > 0:
            embed.add_field(
                name='\u200b', value='**Buy Prices**', inline=False)
            for key, val in sorted(buy_prices.items(), key=lambda x: x[1]):
                embed.add_field(name=key, value=val, inline=True)
        if len(sell_morning_prices) > 0:
            embed.add_field(
                name='\u200b', value='**Sell Morning Prices**', inline=False)
            for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True):
                embed.add_field(name=key, value=val, inline=True)
        if len(sell_afternoon_prices) > 0:
            embed.add_field(
                name='\u200b', value='**Sell Afternoon Prices**', inline=False)
            for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True):
                embed.add_field(name=key, value=val, inline=True)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)


@bot.command()
async def buy(ctx):
    if len(buy_prices) == 0:
        await ctx.send("No buy prices at this time.")
    else:
        date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
        embed = discord.Embed(
            title='Buy Prices',
            color=discord.Colour.dark_blue())
        for key, val in sorted(buy_prices.items(), key=lambda x: x[1]):
            embed.add_field(name=key, value=val, inline=True)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)


@bot.command()
async def sell(ctx):
    if len(sell_morning_prices) == 0 and len(sell_afternoon_prices) == 0:
        await ctx.send("No sell prices at this time.")
    else:
        date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
        embed = discord.Embed(
            title='Sell Prices',
            color=discord.Colour.dark_blue())
        if len(sell_morning_prices) > 0:
            embed.add_field(
                name='\u200b', value='Sell Morning Prices', inline=False)
            for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True):
                embed.add_field(name=key, value=val, inline=True)
        if len(sell_afternoon_prices) > 0:
            embed.add_field(
                name='\u200b', value='Sell Afternoon Prices', inline=False)
            for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True):
                embed.add_field(name=key, value=val, inline=True)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)


@bot.command()
async def add(ctx, op='sell', price='0', selltime=''):
    selltime = selltime.lower()
    if (op != 'buy' and op != 'sell') or not price.isdigit() or (selltime != '' and selltime != 'am' and selltime != 'pm'):
        await ctx.send("Please check your input.")
    else:
        await ctx.send('Added {0.author.name}\'s {1} price of {2}.'.format(ctx, op, price))
        if op == 'buy':
            buy_prices[ctx.author.name] = price
            await buy(ctx)
        else:
            if (datetime.now().hour < 12 and selltime == '') or selltime == 'am':
                sell_morning_prices[ctx.author.name] = int(price)
            elif (datetime.now().hour >= 12 and selltime == '') or selltime == 'pm':
                sell_afternoon_prices[ctx.author.name] = int(price)
            await sell(ctx)


@bot.command()
async def clear(ctx, op='', selltime=''):
    selltime = selltime.lower()
    if (op != '' and op != 'buy' and op != 'sell') or (selltime != '' and selltime != 'am' and selltime != 'pm'):
        await ctx.send("Please check your input.")
    else:
        if op == 'buy':
            buy_prices.pop(ctx.author.name, None)
            await ctx.send("Cleared {0}'s buy price.".format(ctx.author.name))
        elif op == 'sell':
            if selltime == 'am':
                sell_morning_prices.pop(ctx.author.name, None)
                await ctx.send("Cleared {0}'s sell morning price.".format(ctx.author.name))
            elif selltime == 'pm':
                sell_afternoon_prices.pop(ctx.author.name, None)
                await ctx.send("Cleared {0}'s sell afternoon price.".format(ctx.author.name))
            else:
                sell_morning_prices.pop(ctx.author.name, None)
                sell_afternoon_prices.pop(ctx.author.name, None)
                await ctx.send("Cleared {0}'s sell prices.".format(ctx.author.name))
        else:
            buy_prices.pop(ctx.author.name, None)
            sell_morning_prices.pop(ctx.author.name, None)
            sell_afternoon_prices.pop(ctx.author.name, None)
            await ctx.send("Cleared {0}'s buy/sell prices.".format(ctx.author.name))

# Background task to clear prices
@tasks.loop(hours=168)
async def reset_buy_prices():
    await buy_prices.clear()


@reset_buy_prices.before_loop
async def before():
    d = datetime.now()
    t = timedelta((12 - d.weekday()) % 7)
    saturday = d + t
    reset = datetime(year=saturday.year, month=saturday.month,
                     day=saturday.day, hour=23, minute=59, second=59)
    await asyncio.sleep((reset - d).seconds)
    await bot.wait_until_ready()


@tasks.loop(hours=24)
async def reset_sell_prices():
    await sell_morning_prices.clear()
    await sell_afternoon_prices.clear()


@reset_sell_prices.before_loop
async def before():
    d = datetime.now()
    tomorrow = d + timedelta(days=1)
    reset = datetime(year=tomorrow.year, month=tomorrow.month,
                     day=tomorrow.day, hour=reset_time, minute=0, second=0)
    await asyncio.sleep((reset - d).seconds)
    await bot.wait_until_ready()

reset_buy_prices.start()
reset_sell_prices.start()

bot.run(TOKEN)
