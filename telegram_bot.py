import requests
from bs4 import BeautifulSoup
import nest_asyncio
nest_asyncio.apply()
import telegram
from telegram import ForceReply, Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

def mazaneh_from_mazaneh(soup:BeautifulSoup):
  res = soup.find('div', {'id': "Div38"})
  price = res.find('div', {'class': "CurrencyPrice"}).text
  return price

def currency_getter(soup:BeautifulSoup, string:str):
  th_element = soup.find('th', string=string)
  # Find the next td element with the class 'market-price'
  market_price_element = th_element.find_next('td', class_='market-price')
  price = market_price_element.get_text(strip=True)

  return price

def nf_getter(soup:BeautifulSoup, string:str):
  th_element = soup.find('th', string=string)
  # Find the next td element with the class 'market-price'
  market_price_element = th_element.find_next('td', class_='nf')
  price = market_price_element.get_text(strip=True)

  return price


def get_prices():
  url = "https://www.tgju.org/"
  response_status_code = False
  while response_status_code != 200:
      print(f"Requesting To {url}")
      response = requests.get(url)
      response_status_code = response.status_code
      if response_status_code == 200:
          soup = BeautifulSoup(response.text, 'html.parser')
          dollar_price = currency_getter(soup, "دلار")
          mazaneh_price = nf_getter(soup, "آبشده نقدی")
          hobab_price = nf_getter(soup, "حباب آبشده")
          ons_price =  nf_getter(soup, "انس طلا")


          print("Request was sucsessfull")
          return dollar_price, mazaneh_price, hobab_price, ons_price
      else:
        print(f'Error: Unable to fetch the page (status code {response.status_code}) ... Trying again ...')

def format_number(number):
  formatted_number = '{:,}'.format(number)
  return formatted_number

def get_data_formated(dollar_price, mazaneh_price, hobab_price, ons_price):
  mazaneh_integer_price = int(mazaneh_price.replace(",",""))
  gold_gr = format_number(round(int(mazaneh_integer_price/4.331802)/10))

  mazaneh_price = format_number(round(mazaneh_integer_price/10000))
  hobab_price = format_number(round(int(hobab_price.replace(",",""))/10))
  dollar_price = format_number(round(int(dollar_price.replace(",",""))/10))


  # example_data = f"""آبشده فردایی ⏳ {mazaneh_price} خرید 🔵\nحباب آبشده با دلار : {hobab_price}\nگرم طلا : {gold_gr}\nانس طلا : {ons_price}\nدلار تهران : {dollar_price}"""
  example_data = f"""آبشده فردایی ⏳ <b>{mazaneh_price}</b> خرید 🔵\nحباب آبشده با دلار : {hobab_price}\nگرم طلا : {gold_gr}\nانس طلا : {ons_price}\nدلار تهران : {dollar_price}"""


  return example_data

TOKEN = "1104379278:AAGMXNMuzv1pDTWrL_5kRROqZxUgx2oZT5U"
CHANNEL_ID = "-1002094248892"


async def send_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send 'Hello' message to the specified channel."""
    dollar_price, mazaneh_price, hobab_price, ons_price  = get_prices()  # Assuming you have a function to get the current price
    data = get_data_formated(dollar_price, mazaneh_price, hobab_price, ons_price)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=data, parse_mode=telegram.constants.ParseMode.HTML)


async def start_sending(context: ContextTypes.DEFAULT_TYPE):
  # await update.message.reply_text("Hello, you just started the bot!")
  global should_run

  if should_run:
    await send_data(None, context)
  else:
    print("waiting to start ...")

async def stop_sending(context: ContextTypes.DEFAULT_TYPE) :
    print("Stopping the bot!")
    # await update.message.reply_text("Stopping the bot ...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  global should_run
  should_run = True
  context.job_queue.run_repeating(start_sending, interval=60, first=0.1)
  await update.message.reply_text("Hello, you just started the bot!")
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.job_queue.run_once(stop_sending, when=0.1)
  global should_run
  should_run = False
  await update.message.reply_text("Stopping the bot ...")



def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    application.run_polling()


if __name__ == "__main__":
   (main())
