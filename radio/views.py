from datetime import datetime
from radio.models import RadioItem, Radio
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
import subprocess
import simplejson
import threading
import os
import sys
import gdata.youtube
import gdata.youtube.service
import random
import signal
# Create your views here.

# TODO move this out!
YOUTUBE_API_KEY = "AI39si7hH4sRO3JdHIpfudrGd8lyZsXQnXkXrmwX_bq2io7ijeNDUQdGrYT0l77Nao0h9ZoTjjzdK4-kcuRgMUQE8pDCa0q8FA"

def get_radio():
    return Radio.objects.all()[:1].get()

def show_radio(request):
    return render_to_response('radio.html', 
        {"queue": RadioItem.objects.filter(played=False).order_by('queue_time'),
         "playing": get_radio().playing,
         "recent": RadioItem.objects.filter(played=True).order_by('-queue_time')[:10]}, 
        RequestContext(request))

def start_playing(request):
    radio = get_radio()
    if radio.playing == False:
        radio.playing = True
        radio.save()
        next_song()
        return HttpResponse(simplejson.dumps({"result": "success"}))

    return HttpResponse(simplejson.dumps({"result": "already_playing"}))

def stop_playing(request):
    radio = get_radio()

    if request.user.is_staff == False:
        return HttpResponse(status=403)

    radio.playing = False
    radio.save()

    os.kill(radio.vlc_pid, signal.SIGTERM)

    return HttpResponse(simplejson.dumps({"result": "success"}))

def skip_playing(request):
    radio = get_radio()
    os.kill(radio.vlc_pid, signal.SIGTERM)

    return HttpResponse(simplejson.dumps({"result": "success"}))

def get_video_data(video_id):
    """ Use YouTube Gdata API to get the YouTube entry."""
    global YOUTUBE_API_KEY
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.developer_key = YOUTUBE_API_KEY
    yt_service.client_id = 'Morlunk Radio'
    entry = yt_service.GetYouTubeVideoEntry(video_id=video_id)
    return entry

def queue_song(request):
    radio = get_radio()
    try:
        video_id = request.REQUEST["video_id"]

        matches = RadioItem.objects.filter(video_id=video_id)
        if matches.count() == 0:
            # If a match is not found, create a new entry
            entry = get_video_data(video_id)

            item = RadioItem(user_title=entry.media.title.text, video_id=video_id)
            item.save()
        else:
            item = matches.get()
            item.played = False
            item.queue_time = datetime.now()
            item.save()

        # Start playing if not already playing
        if radio.playing == False:
            radio.playing = True
            radio.save()
            next_song()

        response = {"result": "success", "video_title": item.user_title}
    except KeyError:
        response = {"result": "invalid_request"}
    except Exception as e:
        response = {"result": "error", "error": e}
    return HttpResponse(simplejson.dumps(response))

def queue_random(request, count=5):
    iterations = 0
    while iterations < count:
        song_count = RadioItem.objects.all().count()
        index = random.randint(0, song_count)
        
        item = RadioItem.objects.all()[index]
        item.played = False
        item.save()

        iterations += 1
    
    radio = get_radio()

    if radio.playing is False:
        radio.playing = True
        radio.save()
        next_song()
    
    return redirect("/radio/")

def next_song():
    radio = get_radio()
    if radio.playing == True:
        # Start playing
        items = RadioItem.objects.filter(played=False).order_by('queue_time')
        if items.count() > 0:
            play_thread = PlayThread(items[0], next_song)
            play_thread.start()
        else:
            radio.playing = False
            radio.save()

class PlayThread(threading.Thread):
    """ Plays a radio item, and then executes the callback upon completion. """
    def __init__(self, radio_item, callback=None):
        super(PlayThread, self).__init__()
        self.radio_item = radio_item
        self.callback = callback

    def run(self):
        radio = get_radio()

        # Play espeak synth voice
        tts_process = subprocess.Popen(["espeak", "\"Morlunk Radio is now playing %s. You a stupid troll.\"" % self.radio_item.user_title])
        tts_process.wait()

        self.vlc_process = subprocess.Popen(["cvlc", "--no-video", "--play-and-exit", "http://www.youtube.com/watch?v=%s" % self.radio_item.video_id]) # Add extra quotes

        # Set VLC pid
        radio.vlc_pid = self.vlc_process.pid
        radio.save()

        self.vlc_process.wait()

        # Mark played
        self.radio_item.played = True
        self.radio_item.save()

        # Callback after completion
        if self.callback is not None:
            self.callback()

    def kill(self):
        if self.vlc_process is not None and self.vlc_process.poll() is None:
            self.vlc_process.terminate()