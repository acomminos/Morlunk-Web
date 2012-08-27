from datetime import datetime
from radio.models import RadioItem
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
import subprocess
import simplejson
import threading
import os
# Create your views here.

radio_playing = False
play_thread = None

def show_radio(request):
    global radio_playing
    return render_to_response('radio.html', 
        {"queue": RadioItem.objects.filter(played=False).order_by('submission_date'),
         "playing": radio_playing}, 
        RequestContext(request))

def start_playing(request):
    global radio_playing

    if radio_playing is False:
        radio_playing = True
        next_song()

    return HttpResponse(simplejson.dumps({"result": "success"}))

def stop_playing(request):
    global radio_playing, play_thread
    if request.user.is_staff is False:
        return HttpResponse(status=403)

    radio_playing = False

    if play_thread is not None:
        play_thread.kill()

    return HttpResponse(simplejson.dumps({"result": "success"}))

def queue_song(request):
    global radio_playing
    try:
        user_title = request.REQUEST["user_title"]
        video_id = request.REQUEST["video_id"]
        submission_date = datetime.now()
        item = RadioItem(user_title=user_title, video_id=video_id, submission_date=submission_date)
        item.save()

        # Start playing if not already playing
        if radio_playing is False:
            radio_playing = True
            next_song()

        response = {"result": "success"}
    except KeyError:
        response = {"result": "invalid_request"}
    except:
        response = {"result": "error"}
    return HttpResponse(simplejson.dumps(response))

def next_song():
    global play_thread, radio_playing
    if radio_playing is True:
        # Start playing
        items = RadioItem.objects.filter(played=False).order_by('submission_date')
        if items.count() > 0:
            play_thread = PlayThread(items[0], next_song)
            play_thread.start()
        else:
            radio_playing = False

class PlayThread(threading.Thread):
    """ Plays a radio item, and then executes the callback upon completion. """
    def __init__(self, radio_item, callback=None):
        super(PlayThread, self).__init__()
        self.radio_item = radio_item
        self.callback = callback

    def run(self):
        # Play espeak synth voice
        tts_process = subprocess.Popen(["espeak", "\"Morlunk Radio is now playing %s. Submit new tracks at Morlunk.com slash radio.\"" % self.radio_item.user_title])
        tts_process.wait()
        
        self.vlc_process = subprocess.Popen(["cvlc", "--no-video", "--play-and-exit", "http://www.youtube.com/watch?v=%s" % self.radio_item.video_id]) # Add extra quotes
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