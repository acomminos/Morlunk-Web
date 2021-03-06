# -*- coding: utf-8 -*-
from datetime import datetime
from radio.models import RadioItem, Radio
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.template import RequestContext
from django.contrib.auth.models import User
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

    if request.user.is_staff is False:
        return HttpResponse(status=403);

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

    return HttpResponse(simplejson.dumps({"result": "success"}), mimetype="application/json")

def skip_playing(request):

    if request.user.is_authenticated() is False:
        return HttpResponse(simplejson.dumps({"result": "no_auth"}), mimetype="application/json");

    radio = get_radio()

    espeak_notify = subprocess.Popen(["espeak", "\"Skipped by %(first_name)s %(last_name)s.\"" % {"first_name": request.user.first_name, "last_name": request.user.last_name}])
    espeak_notify.wait()

    os.kill(radio.vlc_pid, signal.SIGTERM)

    return HttpResponse(simplejson.dumps({"result": "success"}), mimetype="application/json")

def get_video_data(video_id):
    """ Use YouTube Gdata API to get the YouTube entry."""
    global YOUTUBE_API_KEY
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.developer_key = YOUTUBE_API_KEY
    yt_service.client_id = 'Morlunk Radio'
    entry = yt_service.GetYouTubeVideoEntry(video_id=video_id)
    return entry

def queue_song(request):
    
    if request.user.is_authenticated() is False:
        return HttpResponse(simplejson.dumps({"result": "no_auth"}), mimetype="application/json");

    radio = get_radio()
    try:
        video_id = request.REQUEST["video_id"]

        matches = RadioItem.objects.filter(video_id=video_id)
        if matches.count() == 0:
            # If a match is not found, create a new entry
            entry = get_video_data(video_id)

            item = RadioItem(user_title=entry.media.title.text, video_id=video_id)
            item.queuer = request.user
            item.save()
        else:
            item = matches.get()
            item.played = False
            item.queue_time = datetime.now()
            item.queuer = request.user
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
        response = {"result": "error"}
    return HttpResponse(simplejson.dumps(response))

@login_required
def queue_random(request, count=5):
    iterations = 0
    while iterations < count:
        song_count = RadioItem.objects.all().count()
        index = random.randint(0, song_count)
        
        item = RadioItem.objects.all()[index]
        item.played = False
        item.queuer = request.user
        item.save()

        iterations += 1
    
    radio = get_radio()

    if radio.playing is False:
        radio.playing = True
        radio.save()
        next_song()
    
    return redirect("/radio/")

def status(request):
    radio = get_radio()
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None # Create handler for simplejson to skip date
    queue = RadioItem.objects.filter(played=False).order_by('queue_time')
    queue_list = []
    for radio_item in queue:
        radio_item_dict = model_to_dict(radio_item)
        radio_item_dict["queuer"] = model_to_dict(radio_item.queuer, fields=["first_name", "last_name"]) # Add queuer data to dictionary
        queue_list.append(radio_item_dict)
    recent = RadioItem.objects.filter(played=True).order_by('-queue_time')[:10]
    recent_list = []
    for radio_item in recent:
        radio_item_dict = model_to_dict(radio_item)
        radio_item_dict["queuer"] = model_to_dict(radio_item.queuer, fields=["first_name", "last_name"]) # Add queuer data to dictionary
        recent_list.append(radio_item_dict)
    return HttpResponse(simplejson.dumps({"result": "success", "queue": queue_list, "recent": recent_list, "playing": radio.playing}, default=dthandler), mimetype="application/json")

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
# -*- coding: utf-8 -*-
    def run(self):
        radio = get_radio()

        # Play espeak synth voice
        # Ignore special unicode characters in song name.
        tts_process = subprocess.Popen(["espeak", u'"Morlunk Radio is now playing %(song_name)s. This song was queued by %(first_name)s %(last_name)s."' % {"song_name": unicode(self.radio_item.user_title.encode('utf-8'), errors='ignore'), "first_name": self.radio_item.queuer.first_name, "last_name": self.radio_item.queuer.last_name}])
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
