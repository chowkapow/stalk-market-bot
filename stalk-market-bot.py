import discord
import os
import pytz

from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

buyPrices = {}
sellPrices = {}
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
  buy = '**Buy prices**:\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buyPrices.items(), key=lambda x: x[1]))
  sell = '**Sell prices**:\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sellPrices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send("\nToday's date: {0}\n\n{1}\n{2}".format(date, buy, sell))

@bot.command()
async def buy(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  buy = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buyPrices.items(), key=lambda x: x[1]))
  await ctx.send("Today's date: {0}\n{1}".format(date, buy))

@bot.command()
async def sell(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  sell = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sellPrices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send("Today's date: {0}\n{1}".format(date, sell))

@bot.command()
async def add(ctx, op: str, price: int):
  if op == 'buy':
    buyPrices[ctx.author.name] = price
    current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buyPrices.items(), key=lambda x: x[1]))
  else:
    sellPrices[ctx.author.name] = price
    current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sellPrices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send('Added {0.author.name}\'s {1} price of {2}.\n\n**{3} prices**:\n{4}'.format(ctx, op, price, op.capitalize(), current))

bot.run(TOKEN)
