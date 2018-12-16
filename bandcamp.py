
from flask import Flask
from flask_sslify import SSLify
from flask import request
import telebot
import requests
import wgetter
from lxml import html
import os
import time
import flask


app = Flask(__name__)
sslify = SSLify(app)
TOKEN = '460119009:AAFbL_pJJtqBaBMMjODKYPS-7Xk_p_swS1M'
bot = telebot.TeleBot(TOKEN, threaded=False)



@app.route('/', methods=['POST','GET'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(content_types=['text'])
def handle_start(message):


    #url = 'https://mountainmanrecords.bandcamp.com/track/solitude'

    url = message.text

    response = requests.get(url)
    tree = html.fromstring(response.content)

    cover_url = tree.xpath('//img[@itemprop="image"]/@src')[0]
    meta = tree.xpath('//meta[@name="title"]/@content')[0]

    response = response.text
    audio_url = response.split('"file":{"mp3-128":"')[-1].split('"}')[0]
    meta = meta.split(", by ")
    track = meta[0]
    artist = meta[1]
    tmp_file = response.split('/mp3-128/')[-1].split('?')[0]



    dirc = '/home/vlstv/%s' % artist
    os.mkdir(dirc)

    try:
        wgetter.download(audio_url, outdir='/home/vlstv/%s' % artist)
    except:
        #send error message
        print('error')

    old_file = '%s/%s' % (dirc, tmp_file)
    new_file = '%s/%s - %s.mp3' % (dirc, artist, track)


    try:
        wgetter.download(cover_url, outdir='/home/vlstv/%s' % artist)
    except:
        print('error')

    os.rename(old_file, new_file)

    #send files to chat
    files = os.listdir(dirc)
    for file_path in files:
        if '.mp3' not in file_path:
            img_url = '%s/%s' % (dirc, file_path)

    #send cover
    file = open(img_url, 'rb')
    bot.send_photo(message.chat.id, file)
    os.remove(img_url)

    #send audio
    file = open(new_file, 'rb')
    bot.send_audio(message.chat.id, file)
    os.remove(new_file)
    os.rmdir(dirc)



if __name__ == '__main__':
    #app.run(ssl_context=('/etc/letsencrypt/live/shmuli.tk/fullchain.pem', '/etc/letsencrypt/live/shmuli.tk/privkey.pem'))
    app.run()