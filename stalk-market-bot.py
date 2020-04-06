import discord, os, pytz

from datetime import datetime
from discord.ext import commands 
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

buy_prices = {}
sell_prices = {}
timezone = pytz.timezone('America/Chicago')

@bot.command()
async def info(ctx):
    await ctx.send("Hi! I'll help you find the best prices for turnips.\n\n\
      List of commands:\n\
      $info: List commands\n\
      $all: List all buy/sell prices\n\
      $buy: List buy prices only\n\
      $sell: List sell prices only\n\
      $add: Add your price with \"$add buy n\" or \"$add sell n\"")

@bot.command()
async def all(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  buy = '**Buy Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buy_prices.items(), key=lambda x: x[1]))
  sell = '**Sell Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_prices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send("Today's date: {0}\n\n{1:>12}\n{2:>12}".format(date, buy, sell))

@bot.command()
async def buy(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  buy = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buy_prices.items(), key=lambda x: x[1]))
  await ctx.send("Today's date: {0}\n\n{1:>12}".format(date, buy))

@bot.command()
async def sell(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  sell = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_prices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send("Today's date: {0}\n\n{1:>12}".format(date, sell))

@bot.command()
async def add(ctx, op: str, price: int):
  if op == 'buy':
    buy_prices[ctx.author.name] = price
    current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buy_prices.items(), key=lambda x: x[1]))
  else:
    sell_prices[ctx.author.name] = price
    current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_prices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send('Added {0.author.name}\'s {1} price of {2}.\n\n**{3} Prices**\n{4:>12}'.format(ctx, op, price, op.capitalize(), current))

bot.run(TOKEN)
