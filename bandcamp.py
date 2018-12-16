
from flask import Flask
from flask_sslify import SSLify
from flask import request
import telebot
import requests
import wgetter
from lxml import html
import os
import time



url = 'https://mountainmanrecords.bandcamp.com/track/solitude'

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

def download(audio_url, cover_url, artist, track, tmp_file):

    dirc = '/home/vlstv/%s' % artist
    os.mkdir(dirc)

    try:
        wgetter.download(audio_url, outdir='/home/vlstv/%s' % artist)
    except:
        #send error message
        print('error')

    old_file = '%s/%s' % (dirc, tmp_file)
    new_file = '%s/%s - %s.mp3' % (dirc, artist, track)

    print(old_file)
    print(new_file)

    try:
        wgetter.download(cover_url, outdir='/home/vlstv/%s' % artist)
    except:
        #send error message
        print('error')

    os.rename(old_file, new_file)

download(audio_url, cover_url, meta[1], track, tmp_file)


