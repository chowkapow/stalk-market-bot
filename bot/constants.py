bells = """
```\n
+-------+---------+
| Price | Bells   |
+-------+---------+
| 90    | 360,000 |
+-------+---------+
| 91    | 364,000 |
+-------+---------+
| 92    | 368,000 |
+-------+---------+
| 93    | 372,000 |
+-------+---------+
| 94    | 376,000 |
+-------+---------+
| 95    | 380,000 |
+-------+---------+
 Prices go 90-110
```
"""

default_timezone = "America/Chicago"

error_messages = {
    "empty_buy": "No buy prices at this time.",
    "empty_sell": "No sell prices at this time.",
    "invalid_input": "Invalid input - please try again.",
    "no_data": "No data exists!",
}

faq_message = {
    "\u200b": "Setup",
    "**$timezone**": "Find your timezone [here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568) and type __$timezone timezone__. Default is America/Chicago",
    "**$island**": 'Set your island name. If the name has spaces use quotes, e.g. __$island "island name"__',
    "**$fc**": "Set your friend code, e.g. __$fc SW-####-####-####__",
    "\u200b": "FAQ",
    "1. How does this bot help me?": "This bot keeps track of your turnip prices throughout the week. It will also share your prices to help others. Yay friends!",
    "2. How do I add my prices?": "Type __$add n__. It will add to the buy or sell (morning/afternoon) lists based on your message timestamp. (Note: If you do **not** live in Central timezone, use __$timezone__ command to set your timezone, and __$add__ will adjust accordingly.)",
    "3. It's the afternoon already but I want to add my morning price. Can I still add it?": "Yes! Use __$add n am__ to add your price to the morning price list. Likewise, __$add n pm__ adds your afternoon price.",
    "4. I added my prices. What next?": "Use __$trends__ to see your potential prices of the week!",
    "5. I already cashed out selling my turnips. Why should I still add my prices?": "With __$trends__, you can figure out what your price pattern is. This pattern affects your **NEXT** week's prices! Use __$pattern pattern next__ to add your pattern and __$trends__ will adjust accordingly next week.",
    "6. Anything else I should know?": "You can set your friend code, island name, or dodo code with __$fc__, __$island__, __$dodo__ respectively. Then you can use any of the commands again to share, or use __$info__ to share everything! Refer to __$help__ for all the commands.",
}

help_command = {
    "title": "Help Menu",
    "description": "Find the best prices for turnips!\nWant to contribute? [Github](https://github.com/chowkapow/stalk-market-bot)",
    "help_name": "**$help**",
    "help_value": "List commands",
    "faq_name": "**$faq**",
    "faq_value": "Setup and learn how to use this bot",
    "add_name": "**$add**",
    "add_value": "Add your price with __$add n__, or __$add n am__ and __$add n pm__. See $faq if you are not in Central timezone",
    "today_name": "**$today**",
    "today_value": "List today's prices",
    "history_name": "**$history**",
    "history_value": "List your buy/sell prices of the week",
    "trends_name": "**$trends**",
    "trends_value": "See the trends for your prices via [turnipprophet.io](https://turnipprophet.io)\n**DISCLAIMER**: Site not written by me",
    "pattern_name": "**$pattern**",
    "pattern_value": "Set your pattern from LAST week to improve accuracy for $trends: fl (fluctuating), ss (small spike) , ls (large spike), d (decreasing), e.g. __$pattern fl__. Or use __$pattern fl next__ to record this week's pattern, which will be used for next week's trends",
    "info_name": "**$info**",
    "info_value": "Share your friend code, island name, and/or dodo code, or type __$info username__ to see his/her info. See $faq for setup",
    "dodo_name": "**$dodo**",
    "dodo_value": "Set your dodo code or clear with __$dodo clear__. Resets daily",
    "bells_name": "**$bells**",
    "bells_value": "See how much bells you need to bring for a full haul (assumes fully upgraded inventory)",
    "footer": "Feedback welcome. Contact chowkapow#4085",
}

patterns = {
    "fl": 0,
    "ls": 1,
    "d": 2,
    "ss": 3,
}

patterns_names = {
    "fl": "fluctuating",
    "ls": "large spike",
    "d": "decreasing",
    "ss": "small spike",
}

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
