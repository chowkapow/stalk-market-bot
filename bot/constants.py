# Change reset time here
import pytz

error_messages = {
    "empty_buy": "No buy prices at this time.",
    "empty_sell": "No sell prices at this time.",
    "invalid_input": "Invalid input - please try again.",
    "no_data": "No data exists!",
}

help_command = {
    "title": "Help Menu",
    "description": "I'll help you find the best prices for turnips!",
    "help_name": "**$help**",
    "help_value": "List commands",
    "buy_name": "**$buy**",
    "buy_value": "List buy prices only",
    "sell_name": "**$sell**",
    "sell_value": "List sell prices only",
    "add_name": "**$add**",
    "add_value": 'Add your price with "$add buy n", "$add sell n" *(will add to morning/afternoon based on message timestamp)*, "$add sell n am", "$add sell n pm"',
    "clear_name": "**$clear**",
    "clear_value": 'Clear your prices with "$clear", "$clear buy", "$clear sell", "$clear sell am", "$clear sell pm"',
    "history_name": "**$history**",
    "history_value": "List your buy/sell prices of the week",
    "trends_name": "**$trends**",
    "trends_value": "See the trends for your prices via [turnipprophet.io](https://turnipprophet.io)\n**DISCLAIMER**: Site not written by me",
    "footer": "Feedback welcome. Contact chowkapow#4085",
}

reset_time = 3  # 3 AM

timezone = pytz.timezone("America/Chicago")

weekday_order = {
    "Sun": 0,
    "Mon-AM": 1,
    "Mon-PM": 2,
    "Tue-AM": 3,
    "Tue-PM": 4,
    "Wed-AM": 5,
    "Wed-PM": 6,
    "Thu-AM": 7,
    "Thu-PM": 8,
    "Fri-AM": 9,
    "Fri-PM": 10,
    "Sat-AM": 11,
    "Sat-PM": 12,
}