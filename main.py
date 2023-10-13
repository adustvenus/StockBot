import os.path
from discord.ext import commands
import csv, argparse, sys, pandas, os, discord
from server import keep_alive
import yfinance as yf
from pandas_datareader import data, wb
import datetime


current_time = datetime.datetime.now() 
print (current_time.day) 


bot = commands.Bot(command_prefix='$')

TOKEN = os.getenv('TOKEN')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("words i guess")

@bot.command()


async def info(ctx, stock, type):
  message = "null"
  getInfo = yf.Ticker(stock.upper()).info
  commands = {"sector":getInfo['sector'],"ebitda margins":getInfo['ebitdaMargins'], 
          "profit margins":getInfo['profitMargins'],"operating cashflow":getInfo['operatingCashflow'],
          "operating margins":getInfo['operatingMargins'],"ebitda":getInfo['ebitda'],
          "gross profits":getInfo['grossProfits'], "price":getInfo['currentPrice'],
          "earnings growth":getInfo['earningsGrowth'],"return assets":getInfo['returnOnAssets'],
          "debt":getInfo['totalDebt'],"revenue":getInfo['totalRevenue'],"cps":getInfo['totalCashPerShare'],
          "rps":getInfo['revenuePerShare'],"name" :getInfo['shortName'],"symbol":getInfo['symbol'],
          "market":getInfo['market'],"52 week change":getInfo['52WeekChange'],"projected eps":getInfo['forwardEps']
          ,"total shares":getInfo['sharesOutstanding'],"trailing eps":getInfo['trailingEps'],"forward pe":getInfo['forwardPE'],
          "previous close":getInfo['previousClose'],"regular open":getInfo['regularMarketOpen'],"200 day":getInfo['twoHundredDayAverage'],
          "regular high":getInfo['regularMarketDayHigh'],"50 day":getInfo['fiftyDayAverage'],"open":getInfo['open'],
          "regular low":getInfo['regularMarketDayLow'],"trailing pe":getInfo['trailingPE'],"regular volume":getInfo['regularMarketVolume'],
          "day low":getInfo['dayLow'],"ask":getInfo['ask'],"volume":getInfo['volume'],"52 week high":getInfo['fiftyTwoWeekHigh'],
          "52 week low":getInfo['fiftyTwoWeekLow'],"bid":getInfo['bid'],"tradeable":getInfo['tradeable'],"day high":getInfo['dayHigh'],
          "regular price":getInfo['regularMarketPrice']}

  if type in commands:
    message = str(type)+" "+str(commands[type])
  else:
     message = """Invalid syntax or type, suggested: $info ticker
                \nValid types:
                \n%s
    """,*valid(sep = ", ")
  await ctx.channel.send(message)

@bot.command()
async def register(ctx):
  author = str(ctx.author.id)
  header = ['Ticker', 'Shares', 'Total_Value']
  filename = (author + '.csv')

  if os.path.exists(filename):
    await ctx.channel.send("You have already registered!")
  else:
    with open(filename, 'w', newline="") as file:
      csvwriter = csv.writer(file)
      csvwriter.writerow(header)
    with open('Paper.csv', 'a', newline="") as file:
      writer = csv.writer(file)
      writer.writerow([author, 1000000])
    with open('Paycheck.csv', 'a', newline="") as file:
      writer = csv.writer(file)
      writer.writerow([author, 0])
    await ctx.channel.send("Registered!")
    

@bot.command()
async def buy(ctx, stock, amount):
  author = str(ctx.author.id)
  filename = (author + '.csv')
  shares = int(amount)
  ticker = stock.upper()
  stock_info = yf.Ticker(ticker.upper()).info
  market_price = float(stock_info['regularMarketPrice'])
  
  if os.path.exists(filename) == False:
    await ctx.channel.send("You need to register first! Use $register to do so.")

    
  else:
    with open("Paper.csv", "r") as op:
      dt = csv.DictReader(op)
      up_dt = []
      for r in dt:
          if (str(r['user_id']) == author) and (float(r['balance'])-(market_price*shares) >= 0):
            row = {'user_id': r['user_id'],
                 'balance': (float(r['balance'])-(market_price*shares))}
            await ctx.channel.send(str(amount) + ' shares bought at $'+ str(market_price) + ', totaling $' + str(float(shares)*float(market_price)))
          elif (str(r['user_id']) == author) and (float(r['balance'])-(market_price*shares) < 0):
            await ctx.channel.send('You do not have enough funds to purchase these shares!')
          else:
            row = {'user_id': r['user_id'],
                 'balance': r['balance']}
            
          up_dt.append(row)
        
      with open("Paper.csv", "w", newline='') as op:
        headers = ['user_id', 'balance']
        data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
        data.writerow(dict((heads, heads) for heads in headers))
        data.writerows(up_dt)

    
    with open(author+".csv", "r") as op:
      dt = csv.DictReader(op)
      up_dt = []
      check4ticker = 0
      for r in dt:
        row = {'Ticker': r['Ticker'],
               'Shares': r['Shares'],
               'Total_Value': r['Total_Value']}
        if r['Ticker'] == ticker:
          row['Shares'] = int(r['Shares']) + shares
          row['Total_Value'] = float(r['Total_Value']) + float(r['Shares'])*float(market_price)
          check4ticker = 1
        up_dt.append(row)
      if check4ticker == 0:
          row2 = {'Ticker': ticker,
               'Shares': shares,
               'Total_Value': shares*float(market_price)}
          up_dt.append(row2)

      
    with open(author+".csv", "w", newline='') as op:
      headers = ['Ticker', 'Shares', 'Total_Value']
      data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
      data.writerow(dict((heads, heads) for heads in headers))
      data.writerows(up_dt)


@bot.command()
async def sell_list(ctx):
  author = str(ctx.author.id)
  up_dt = []
  with open(author+".csv", "r") as op:
    dt = csv.DictReader(op)
    for r in dt:
      stock_info = yf.Ticker(r['Ticker']).info
      market_price = float(stock_info['regularMarketPrice'])

      row = {'Ticker': r['Ticker'],
             'Shares': r['Shares'],
             'Total_Value':(market_price*int(r['Shares']))}
      
      up_dt.append(row)
  await ctx.channel.send(up_dt)

@bot.command()
async def sell(ctx, stock, amount):
  author = str(ctx.author.id)
  filename = (author + '.csv')
  shares = int(amount)
  ticker = stock.upper()
  stock_info = yf.Ticker(ticker.upper()).info
  market_price = float(stock_info['regularMarketPrice'])

  with open(author+".csv", "r") as op:
    dt = csv.DictReader(op)
    up_dt = []
    SOLD = 0
    for r in dt:
      row = {'Ticker': r['Ticker'],
             'Shares': r['Shares'],
             'Total_Value': float(r['Shares'])*market_price}
      if r['Ticker'] == ticker:
        if shares > int(r['Shares']):
          await ctx.channel.send("You cannot sell more than you own, try again.")
          up_dt.append(row)
        elif shares < int(r['Shares']):
          row['Shares'] = int(r['Shares']) - shares
          row['Total_Value'] = float(r['Total_Value']) - int(row['Shares'])*market_price
          sell_value=shares*market_price
          up_dt.append(row)
          SOLD = 1
        elif shares == int(r['Shares']):
          sell_value=shares*market_price
          SOLD = 1
      else:
        up_dt.append(row)

    with open(author+".csv", "w", newline='') as op:
      headers = ['Ticker', 'Shares', 'Total_Value']
      data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
      data.writerow(dict((heads, heads) for heads in headers))
      data.writerows(up_dt)

  with open("Paper.csv", "r") as op:
    dt = csv.DictReader(op)
    up_dt = []
    for r in dt:
        if (str(r['user_id']) == author and SOLD == 1):
          row = {'user_id': r['user_id'],
               'balance': float(r['balance'])+sell_value}
          await ctx.channel.send(str(amount) + ' shares sold at $'+ str(market_price) + ', totaling $' + str(float(shares)*float(market_price)))

        else:
          row = {'user_id': r['user_id'],
               'balance': r['balance']}
        up_dt.append(row)
      
    with open("Paper.csv", "w", newline='') as op:
      headers = ['user_id', 'balance']
      data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
      data.writerow(dict((heads, heads) for heads in headers))
      data.writerows(up_dt)


@bot.command()
async def refresh(ctx):
  author = str(ctx.author.id)
 
  with open(author+".csv", "r") as op:
      dt = csv.DictReader(op)
      up_dt = []
      for r in dt:
        row = {'Ticker': r['Ticker'],
               'Shares': r['Shares'],
               'Total_Value': r['Total_Value']}
        stock_info = yf.Ticker(r['Ticker'].upper()).info
        market_price = float(stock_info['regularMarketPrice'])

        row['Total_Value'] = int(row['Shares'])*market_price
        up_dt.append(row)
      
  with open(author+".csv", "w", newline='') as op:
    headers = ['Ticker', 'Shares', 'Total_Value']
    data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
    data.writerow(dict((heads, heads) for heads in headers))
    data.writerows(up_dt)
  await ctx.channel.send("Current market prices and user balances refreshed")
  
@bot.command()
async def portfolio_bal(ctx):
  author = str(ctx.author.id)
  Portfolio_Value = 0
  with open(author+".csv", "r") as op:
      dt = csv.DictReader(op)
      for r in dt:
        row = {'Ticker': r['Ticker'],
               'Shares': r['Shares'],
               'Total_Value': r['Total_Value']}
        stock_info = yf.Ticker(r['Ticker'].upper()).info
        market_price = float(stock_info['regularMarketPrice'])
        row['Total_Value'] = int(row['Shares'])*market_price
        Portfolio_Value += float(row['Total_Value'])
      await ctx.channel.send("Your current portfolio is worth $%.2f" %Portfolio_Value)

@bot.command()
async def net_worth(ctx):
  author = str(ctx.author.id)
  Portfolio_Value = 0
  free_cash = 0
  with open(author+".csv", "r") as op:
      dt = csv.DictReader(op)
      for r in dt:
        row = {'Ticker': r['Ticker'],
               'Shares': r['Shares'],
               'Total_Value': r['Total_Value']}
        stock_info = yf.Ticker(r['Ticker'].upper()).info
        market_price = float(stock_info['regularMarketPrice'])
        row['Total_Value'] = int(row['Shares'])*market_price
        Portfolio_Value += float(row['Total_Value'])
  with open("Paper.csv", "r") as op:
      dt = csv.DictReader(op)
      for r in dt:
        if (str(r['user_id']) == author):
          row = {'user_id': r['user_id'],
             'balance': r['balance']}
          free_cash = float(r['balance'])

  NET = free_cash + Portfolio_Value
  await ctx.channel.send("Your current Net Worth is $% .2f" %NET)


@bot.command()
async def bankrupt(ctx):
  author = str(ctx.author.id)
  a = ["y","yes"]
  header = ['Ticker', 'Shares', 'Total_Value']
  await ctx.channel.send("Are you sure you wish to declare Bankruptcy and reset your account? (y/n)")
  msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
  if msg.content in a:
    with open("Paper.csv", "r") as op:
      dt = csv.DictReader(op)
      up_dt = []
      for r in dt:
        if (str(r['user_id']) == author):
          row = {'user_id': r['user_id'],
               'balance': 1000000}
        else:
          row = {'user_id': r['user_id'],
               'balance': r['balance']}
        up_dt.append(row)
      
    with open("Paper.csv", "w", newline='') as op:
      headers = ['user_id', 'balance']
      data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
      data.writerow(dict((heads, heads) for heads in headers))
      data.writerows(up_dt)
    
    with open(author+'.csv', 'w', newline="") as file:
      csvwriter = csv.writer(file)
      csvwriter.writerow(header)
    await ctx.channel.send("BANKRUPTCY!! (Account reset)")

  if msg.content not in a:
    await ctx.channel.send("Bankruptcy abandoned, happy trading!")

@bot.event
async def on_message(message):
  paycheck = 0
  author = str(message.author.id)
  if message.author.bot:
        return
  else:
    with open("Paycheck.csv") as file:
      dt = csv.DictReader(file)
      up_dt = []
      PAYED = 0
      for r in dt:
        if r['user_id'] == author:
          row = {'user_id': r['user_id'],
                   'work': r['work']}
          row['work'] = int(r['work'])+1
          if int(row['work']) >= 10:
            row['work'] = 0
            PAYED = 1              
        else:
          row = {'user_id': r['user_id'],
                   'work': r['work']}
        up_dt.append(row)

        
    with open("Paycheck.csv", "w", newline='') as file:
      headers = ['user_id', 'work']
      data = csv.DictWriter(file, delimiter=',', fieldnames=headers)
      data.writerow(dict((heads, heads) for heads in headers))
      data.writerows(up_dt)

  if PAYED == 1:
    with open("Paper.csv", "r") as op:
      dt = csv.DictReader(op)
      up_dt = []
      for r in dt:
        row = {'user_id': r['user_id'],
           'balance': r['balance']}
        if (str(r['user_id']) == author):
          row['balance'] = float(r['balance']) +50000
        up_dt.append(row)
    
    with open("Paper.csv", "w", newline='') as op:
      headers = ['user_id', 'balance']
      data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
      data.writerow(dict((heads, heads) for heads in headers))
      data.writerows(up_dt)
      await message.channel.send("You got paid your paycheck of $50,000!")
  await bot.process_commands(message)

print("Server Running.")
keep_alive()
bot.run(TOKEN)
