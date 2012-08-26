from datetime import datetime
from radio.models import RadioItem
from django.http import HttpResponse
import subprocess
import simplejson
# Create your views here.

radio_playing = False
vlc_process = None

def start_playing(request):
	if request.user.is_staff() is False:
		return HttpResponse(status=403)

	next_song()

	radio_playing = True


def stop_playing(request):
	if request.user.is_staff() is False:
		return HttpResponse(status=403)

	

def queue_song(request):
	try:
		user_title = request.REQUEST["user_title"]
		video_id = request.REQUEST["video_id"]
		submission_date = datetime.now()
		item = RadioItem(user_title=user_title, video_id=video_id, submission_date=submission_date)
		item.save(
)		response = {"result": "success"}
	except KeyError:
		response = {"result": "invalid_request"}
	except:
		response = {"result": "error"}
	return HttpResponse(simplejson.dumps(response))

def next_song():
	if vlc_process is None:
		# Start playing
		item = RadioItem.objects.filter(played=False).order_by()
		vlc_process = subprocess.Popen(["youplay", item.video_id])