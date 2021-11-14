from flask import Flask
from flask import request
import telebot
import requests
import wgetter
from lxml import html
import os
import flask
import re
import html as uhtml
import json
from settings import GROUP_ID, TOKEN, WEBHOOK_URL

download_dir ='/tmp'

app = Flask(__name__)
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

def get_meta(response):
    tree = html.fromstring(response.text)
    cover = tree.xpath('//meta[@property="og:image"]/@content')[0]
    meta = tree.xpath('//meta[@name="title"]/@content')[0]
    meta = meta.split(', by ')
    return {'artist': meta[1], 'album': meta[0], 'cover': cover}

def get_song_list(response):
    response = uhtml.unescape(response.text)
    songs  = re.findall('trackinfo\":[^]]*]', response)[0].replace('trackinfo\":', '')
    songs = json.loads(songs)
    song_list = []
    for song in songs:
        try:
            song_list.append({0: [song["title"], song["file"]["mp3-128"]]})
        except:
            pass
    return song_list

def get_songs(url, chat_id):
    response = requests.get(url)
    info = get_meta(response)
    song_list = get_song_list(response)
    info.update({'songs': song_list})
    return info

@bot.message_handler(content_types=['text'])
def handle_start(message):

    #check if url is valid
    if re.match(r'https:\/\/*.*\.bandcamp\.com\/track\/*.*', message.text):
        try:
            url = message.text
            meta = get_songs(url, message.chat.id)
            artist = meta['artist']
            cover_url = meta['cover']
            album = meta['album']
            song_url = meta['songs'][0][0][1]
            song = meta['songs'][0][0][0]


            wgetter.download(song_url, outdir=download_dir)
            wgetter.download(cover_url, outdir=download_dir)

            audio_file = download_dir + '/' + song_url.split('/mp3-128/')[-1].split('?')[0]
            cover_file = download_dir + '/' + cover_url.split('img/')[1]

            cover = open(cover_file, 'rb')
            bot.send_photo(GROUP_ID, cover, caption='{} - {}'.format(artist, album), disable_notification=True)
            os.remove(cover_file)

            audio = open(audio_file, 'rb')
            bot.send_audio(GROUP_ID, audio, performer=artist, title=song, disable_notification=False)
            os.remove(audio_file)
        except Exception as e:
            bot.send_message(message.chat.id, e)

bot.set_webhook(WEBHOOK_URL)

if __name__ == '__main__':
    app.run()
