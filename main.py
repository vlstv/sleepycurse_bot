from flask import Flask
from flask import request
import telebot
import requests
import wgetter
from lxml import html
import os
import time
import flask
import re
import sys
import mutagen
from mutagen.easyid3 import EasyID3
from local_settings import *

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

@bot.message_handler(content_types=['text'])
def handle_start(message):

    #check if url is valid 
    if re.match(r'https:\/\/*.*\.bandcamp\.com\/track\/*.*', message.text):
        
        url = message.text

        try:    
            response = requests.get(url)
            tree = html.fromstring(response.content)
            #get song cover
            cover_url = tree.xpath('//img[@itemprop="image"]/@src')[0]
            #get song and artist from metadata
            meta = tree.xpath('//meta[@name="title"]/@content')[0]

            response = response.text
            #get audio url
            audio_url = response.split('"file":{"mp3-128":"')[-1].split('"}')[0]
            meta = meta.split(", by ")
            track = meta[0] #track name
            artist = meta[1] #artist name
            tmp_file = response.split('/mp3-128/')[-1].split('?')[0]
        except:
	    sys.exit()


        dirc = UPLOAD_DIR + artist
        #create artists's dir
        try:
            os.mkdir(dirc)
            #download audio to created dir
            wgetter.download(audio_url, outdir=dirc)
        except:
            bot.send_message(message.chat.id, 'error occured while downloading track')

        old_file = '%s/%s' % (dirc, tmp_file)
        #create new name for downloaded file:
        new_file = '%s/%s - %s.mp3' % (dirc, artist, track)


        try:
            #download song cover
            wgetter.download(cover_url, outdir=dirc)
        except:
            bot.send_message(message.chat.id, 'error occured while downloading image')
        #rename audio file
        os.rename(old_file, new_file)
        
        try:
            audiofile = EasyID3(new_file)
            audiofile['artist'] = artist
            audiofile['title'] = track
            audiofile.save()
        except mutagen.id3.ID3NoHeaderError:
            audiofile = mutagen.File(new_file, easy=True)
            audiofile.add_tags()
            audiofile['artist'] = artist
            audiofile['title'] = track
            audiofile.save()

        #send files to chat
        files = os.listdir(dirc)
        for file_path in files:
            if '.mp3' not in file_path:
                img_url = '%s/%s' % (dirc, file_path)

        #send cover
        try:
            file = open(img_url, 'rb')
            bot.send_photo(BOT_TAG, file)
            #delete cover after sending
            os.remove(img_url)

            #send audio
            file = open(new_file, 'rb')
            bot.send_audio(BOT_TAG, file)
            #delete audio and folser after sending 
            os.remove(new_file)
            os.rmdir(dirc)
        except:
            try:
                #delete all files if upload fails 
                os.remove(img_url)
                os.remove(new_file)
                os.rmdir(dirc)
            except:
                print('upload failed')


    else:
        bot.send_message(message.chat.id, 'url is not valid')


bot.set_webhook(WEBHOOK_URL)

if __name__ == '__main__':
    app.run(ssl_context=(SSL_FULLCHAIN, SSL_PRIVKEY))
    app.run()
