import asyncio, discord, os, pytz

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

buy_prices = {}
sell_morning_prices = {}
sell_afternoon_prices = {}
timezone = pytz.timezone('America/Chicago')
# Change reset time here
reset_time = 3 # 3 AM

# Bot commands
@bot.command()
async def info(ctx):
    await ctx.send("Hi! I'll help you find the best prices for turnips.\n\n\
      List of commands:\n\
      $info: List commands\n\
      $all: List all buy/sell prices\n\
      $buy: List buy prices only\n\
      $sell: List sell prices only\n\
      $add: Add your price with \"$add buy n\" or \"$add sell n\"\n\
      $clear: Clear your buy/sell prices\n")

@bot.command()
async def all(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  buy = '**Buy Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buy_prices.items(), key=lambda x: x[1]))
  sell_m = '**Sell Morning Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True))
  sell_a = '**Sell Afternoon Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send("Today's date: {0}\n\n{1:>12}\n{2:>12}\n{3:>12}".format(date, buy, sell_m, sell_a))

@bot.command()
async def buy(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  buy = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buy_prices.items(), key=lambda x: x[1]))
  await ctx.send("Today's date: {0}\n\n{1:>12}".format(date, buy))

@bot.command()
async def sell(ctx):
  date = timezone.localize(datetime.now()).strftime("%d/%m %I:%M %p %Z")
  sell_m = '**Sell Morning Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True))
  sell_a = '**Sell Afternoon Prices**\n' + ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send("Today's date: {0}\n\n{1:>12}\n{2:>12}".format(date, sell_m, sell_a))

@bot.command()
async def add(ctx, op: str, price: int):
  if op == 'buy':
    buy_prices[ctx.author.name] = price
    current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(buy_prices.items(), key=lambda x: x[1]))
  else:
    if datetime.now().hour < 12:
      sell_morning_prices[ctx.author.name] = price
      current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_morning_prices.items(), key=lambda x: x[1], reverse=True))
    else:
      sell_afternoon_prices[ctx.author.name] = price
      current = ''.join('{}:\t{}\n'.format(key, val) for key, val in sorted(sell_afternoon_prices.items(), key=lambda x: x[1], reverse=True))
  await ctx.send('Added {0.author.name}\'s {1} price of {2}.\n\n**{3} Prices**\n{4:>12}'.format(ctx, op, price, op.capitalize(), current))

@bot.command()
async def clear(ctx):
  buy_prices.pop(ctx.author.name, None)
  sell_morning_prices.pop(ctx.author.name, None)
  sell_afternoon_prices.pop(ctx.author.name, None)
  await ctx.send("Cleared {0}'s buy/sell prices.".format(ctx.author.name))

# Background task to clear prices
@tasks.loop(hours=24)
async def reset_prices():
  buy_prices.clear()
  sell_prices.clear()

@reset_prices.before_loop
async def before():
  tomorrow = datetime.now() + timedelta(days=1)
  reset = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=reset_time, minute=0, second=0)
  await asyncio.sleep((reset - datetime.now()).seconds)
  await bot.wait_until_ready()

reset_prices.start()

bot.run(TOKEN)
