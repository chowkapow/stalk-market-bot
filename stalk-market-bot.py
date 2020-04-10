import asyncio
import discord
import json
import logging
import os
import pytz
import sys
import urllib.request

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv

env = 'dev' if len(sys.argv) == 1 else sys.argv[1]
# Change reset time here
reset_time = 3  # 3 AM

weekday_order = {
    'Sun': 0,
    'Mon-AM': 1,
    'Mon-PM': 2,
    'Tue-AM': 3,
    'Tue-PM': 4,
    'Wed-AM': 5,
    'Wed-PM': 6,
    'Thu-AM': 7,
    'Thu-PM': 8,
    'Fri-AM': 9,
    'Fri-PM': 10,
    'Sat-AM': 11,
    'Sat-PM': 12
}

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


def is_turnip_trader():
    async def predicate(ctx):
        return "Turnip Trader" in [r.name for r in ctx.author.roles]
    return commands.check(predicate)


def read_json(filename):
    with open(filename) as readfile:
        data = json.load(readfile)
        return data


def write_json(name, op, price, selltime):
    date = datetime.now()
    filename = env + '_data.json'
    data = read_json(filename)
    if name not in data.keys():
        data[name] = {}
    if op == 'buy':
        key = 'Sun'
    else:
        day = date.strftime('%a')
        selltime = date.strftime('%p') if selltime == '' else selltime.upper()
        key = day + '-' + selltime
    data[name][key] = price
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=2)


def tiny_url(url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urllib.request.urlopen(apiurl + url).read()
    return tinyurl.decode("utf-8")


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
    embed.add_field(
        name='**$history**', value='List your buy/sell prices of the week', inline=False)
    embed.add_field(
        name='**$trends**', value='See the trends for your prices via [turnipprophet.io](https://turnipprophet.io)\n**DISCLAIMER**: NOT written by me', inline=False
    )
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
            i = 0
            for key, val in sorted(buy_prices.items(), key=lambda x: x[1]):
                i += 1
                embed.add_field(name=key if i > 1 else 'Lowest', value=val if i > 1 else str("""```py\n{0} - {1}```""".format(key, val)),
                                inline=True if i > 1 else False)
        if len(sell_morning_prices) > 0:
            embed.add_field(
                name='\u200b', value='**Sell Morning Prices**', inline=False)
            i = 0
            for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True):
                i += 1
                embed.add_field(name=key if i > 1 else 'Highest', value=val if i > 1 else str("""```py\n{0} - {1}```""".format(key, val)),
                                inline=True if i > 1 else False)
        if len(sell_afternoon_prices) > 0:
            embed.add_field(
                name='\u200b', value='**Sell Afternoon Prices**', inline=False)
            i = 0
            for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True):
                i += 1
                embed.add_field(name=key if i > 1 else 'Highest', value=val if i > 1 else str("""```py\n{0} - {1}```""".format(key, val)),
                                inline=True if i > 1 else False)
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
        i = 0
        for key, val in sorted(buy_prices.items(), key=lambda x: x[1]):
            i += 1
            embed.add_field(name=key if i > 1 else 'Lowest', value=val if i > 1 else str("""```py\n{0} - {1}```""".format(key, val)),
                            inline=True if i > 1 else False)
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
            i = 0
            for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True):
                i += 1
                embed.add_field(name=key if i > 1 else 'Highest', value=val if i > 1 else str("""```py\n{0} - {1}```""".format(key, val)),
                                inline=True if i > 1 else False)
        if len(sell_afternoon_prices) > 0:
            embed.add_field(
                name='\u200b', value='Sell Afternoon Prices', inline=False)
            i = 0
            for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True):
                i += 1
                embed.add_field(name=key if i > 1 else 'Highest', value=val if i > 1 else str("""```py\n{0} - {1}```""".format(key, val)),
                                inline=True if i > 1 else False)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)


@bot.command()
async def add(ctx, op: str, price: int, selltime=''):
    selltime = selltime.lower()
    if (op != 'buy' and op != 'sell') or (selltime != '' and selltime != 'am' and selltime != 'pm'):
        await ctx.send("Invalid input - please try again.")
    else:
        await ctx.send('Added {0}\'s {1} price of {2}.'.format(ctx.author.name, op, price))
        write_json(ctx.author.name, op, price, selltime)
        if op == 'buy':
            buy_prices[ctx.author.name] = price
            await buy(ctx)
        else:
            if (datetime.now().hour < 12 and selltime == '') or selltime == 'am':
                sell_morning_prices[ctx.author.name] = price
            elif (datetime.now().hour >= 12 and selltime == '') or selltime == 'pm':
                sell_afternoon_prices[ctx.author.name] = price
            await sell(ctx)


@bot.command(name='clear')
async def clearPrices(ctx, op='', selltime=''):
    selltime = selltime.lower()
    if (op != '' and op != 'buy' and op != 'sell') or (selltime != '' and selltime != 'am' and selltime != 'pm'):
        await ctx.send("Invalid input - please try again.")
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


@bot.command()
async def history(ctx):
    data = read_json(env + '_data.json')
    user = ctx.author.name
    if user in data.keys():
        date = timezone.localize(datetime.now()).strftime("%B %d, %I:%M %p %Z")
        embed = discord.Embed(title=user + '\'s Prices',
                              color=discord.Colour.dark_blue())
        for key, val in sorted(data[user].items(), key=lambda x: weekday_order[x[0]]):
            embed.add_field(name=key, value=val, inline=False)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)
    else:
        await ctx.send('No data exists!')


@bot.command()
async def trends(ctx):
    data = read_json(env + '_data.json')
    user = ctx.author.name
    prices = ''
    if user in data.keys():
        missing_days = set(weekday_order.keys()) - set(data[user].keys())
        for d in missing_days:
            data[user][d] = ''
        for key, val in sorted(data[user].items(), key=lambda x: weekday_order[x[0]]):
            prices += str(val) + '.'
        url = 'https://turnipprophet.io/index.html?prices={}'.format(prices)
        await ctx.send('{}\'s trends here: {}'.format(ctx.author.name, tiny_url(url)))
    else:
        await ctx.send('No data exists!')


@bot.command()
@is_turnip_trader()
async def admin_add(ctx, name: str, op: str, price: int, selltime=''):
    selltime = selltime.lower()
    await ctx.send('Added {0}\'s {1} price of {2}.'.format(name, op, price))
    write_json(name, op, price, selltime)
    if op == 'buy':
        buy_prices[name] = price
        await buy(ctx)
    else:
        if (datetime.now().hour < 12 and selltime == '') or selltime == 'am':
            sell_morning_prices[name] = price
        elif (datetime.now().hour >= 12 and selltime == '') or selltime == 'pm':
            sell_afternoon_prices[name] = price
        await sell(ctx)


@bot.command()
@is_turnip_trader()
async def admin_clear(ctx, name='', op='', selltime=''):
    selltime = selltime.lower()
    if op == 'buy':
        buy_prices.pop(name, None)
        await ctx.send("Cleared {0}'s buy price.".format(name))
    elif op == 'sell':
        if selltime == 'am':
            sell_morning_prices.pop(name, None)
            await ctx.send("Cleared {0}'s sell morning price.".format(name))
        elif selltime == 'pm':
            sell_afternoon_prices.pop(name, None)
            await ctx.send("Cleared {0}'s sell afternoon price.".format(name))
        else:
            sell_morning_prices.pop(name, None)
            sell_afternoon_prices.pop(name, None)
            await ctx.send("Cleared {0}'s sell prices.".format(name))
    elif name != '':
        buy_prices.pop(name, None)
        sell_morning_prices.pop(name, None)
        sell_afternoon_prices.pop(name, None)
        await ctx.send("Cleared {0}'s buy/sell prices.".format(name))
    else:
        buy_prices.clear()
        sell_morning_prices.clear()
        sell_afternoon_prices.clear()
        await ctx.send("Cleared all prices.")


@bot.command()
@is_turnip_trader()
async def admin_restore(ctx):
    date = datetime.now()
    data = read_json(env + '_data.json')
    today = date.strftime('%a')
    for user, user_data in data.items():
        if today == 'Sun':
            if today in user_data.keys():
                buy_prices[user] = user_data[today]
        else:
            if (today + '-AM') in user_data.keys():
                sell_morning_prices[user] = user_data[today + '-AM']
            if (today + '-PM') in user_data.keys():
                sell_afternoon_prices[user] = user_data[today + '-PM']
    if len(buy_prices) > 0 or len(sell_morning_prices) > 0 or len(sell_afternoon_prices) > 0:
        await ctx.send("Restore complete.")
        await all(ctx)
    else:
        await ctx.send("No data to restore.")


@bot.event
async def on_command_error(ctx, error):
    await ctx.send("Invalid input - please try again.")

# Background tasks to clear prices
@tasks.loop(hours=168)
async def reset_buy_prices():
    buy_prices.clear()
    with open(env + '_data.json', 'w') as outfile:
        json.dump({}, outfile)


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
    sell_morning_prices.clear()
    sell_afternoon_prices.clear()


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
