from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from saucenao import SauceNao
import pyweathercn
import requests
import re
import logging
import json
import os
import time


def _dog(bot, update):
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    url = ''
    while file_extension not in allowed_extension:
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    bot.sendPhoto(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, photo=url)


def _cat(bot, update):
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    url = ''
    while file_extension not in allowed_extension:
        contents = requests.get('http://aws.random.cat/meow').json()
        url = contents['file']
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    bot.sendPhoto(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, photo=url)


def _weather(bot, update):
    CODE = {200001: 'success',
            400001: 'city not found.',
            400002: 'city param error',
            400003: 'day out of range',
            401001: 'A valid key is required to access this API',
            404001: 'The url you requested is invalid',
            429001: 'You have exceeded your request limit!',
            500001: 'craw denied',
            500002: 'Unknown error. Please contact @BennyThink via Telegram.'}

    print(update.message)
    chat_id = update.message.chat_id
    args = update.message.text.split()[1:]
    if len(args) == 0:
        bot.sendMessage(chat_id=chat_id, text='give me a city name')
        return
    elif len(args) == 2:
        city = args[0]
        day = args[1]
    else:
        city = args[0]
        day = 0

    weather = pyweathercn.Weather(city)
    if 'code' in weather.data:
        bot.sendMessage(chat_id=chat_id, text=CODE[weather.data['code']])
    else:
        bot.sendMessage(chat_id=chat_id, text=weather.forecast(day=day) + '\n\n' + weather.tip()[len(city):])


def _imageSearch(bot, update):
    imageName = bot.getFile(update.message.photo[-1].file_id).download(str(time.time()))
    saucenao = SauceNao(directory='', databases=999, minimum_similarity=65, combine_api_types=False, api_key=''
                        , exclude_categories='', move_to_categories=False, use_author_as_category=False, output_type=
                        SauceNao.API_HTML_TYPE, start_file='', log_level=logging.ERROR, title_minimum_similarity=90)
    filtered_results = saucenao.check_image(imageName, saucenao.API_JSON_TYPE)
    results = json.loads(filtered_results)['results']
    for result in results:
        similarity = result['header']['similarity']
        url = result['data']['ext_urls'][0]
        bot.sendMessage(chat_id=update.message.chat_id, text=url)
        bot.sendMessage(chat_id=update.message.chat_id, text="\n\n\t *similarity:* "+similarity, parse_mode='Markdown')

    os.remove(imageName)


def _list(bot, update):
    list = "all command: \n\
    /start /list /help - get command list \n\
    /randomDog - get random dog \n\
    /randomCat - get random cat \n\
    /weather <cityName> [number<=5](default=0) - get weather after {number} day \n\
    {image} - reverse image search "

    '''
    markup =
    itembtn1 = bot.types.KeyboardButton('randomCat', _cat)
    itembtn2 = bot.types.KeyboardButton('randomDog', _dog)
    markup.add(itembtn1, itembtn2)
    '''

    bot.sendMessage(chat_id=update.message.chat_id, text=list)


def main():
    token = '562526669:AAHWcpFQrIkGd2bZt1YkKUEmdJve0JOs_pQ'
    updater = Updater(token=token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('list', _list))
    dispatcher.add_handler(CommandHandler('help', _list))
    dispatcher.add_handler(CommandHandler('start', _list))
    dispatcher.add_handler(CommandHandler('randomDog', _dog))
    dispatcher.add_handler(CommandHandler('randomCat', _cat))
    dispatcher.add_handler(CommandHandler('weather', _weather))
    dispatcher.add_handler(MessageHandler(Filters.photo, _imageSearch))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
