from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template import RequestContext, Template

from paoman.models import PaomanAccount

# Create your views here.

def play_game(request):
	user = request.user
	# Make sure user is logged in.
	if user.is_authenticated():
		# Make sure user has a super paoman account
		if PaomanAccount.objects.filter(user=user).count() > 0:
			paoman = PaomanAccount.objects.get(user=user)
			return render_to_response("paoman.html", 
									{'paoman': paoman},
									RequestContext(request))
		else:
			return HttpResponse(status=404)
	else:
		return HttpResponse(status=404)