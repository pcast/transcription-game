import sys
import json
import datetime
import random

from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.db.models import Q

from webhindigame.models import Word,Score,Transcript,Action

# ------------------------- accessories ---------------------------------------

# This is a straightforward implementation of a well-known algorithm, and thus
# probably shouldn't be covered by copyright to begin with. But in case it is,
# the author (Magnus Lie Hetland) has, to the extent possible under law,
# dedicated all copyright and related and neighboring rights to this software
# to the public domain worldwide, by distributing it under the CC0 license,
# version 1.0. This software is distributed without any warranty. For more
# information, see <http://creativecommons.org/publicdomain/zero/1.0>
def levenshtein(a,b):
	"Calculates the Levenshtein distance between a and b."
	n, m = len(a), len(b)
	if n > m:
		# Make sure n <= m, to use O(min(n,m)) space
		a,b = b,a
		n,m = m,n
		
	current = range(n+1)
	for i in range(1,m+1):
		previous, current = current, [i]+[0]*n
		for j in range(1,n+1):
			add, delete = previous[j]+1, current[j-1]+1
			change = previous[j-1]
			if a[j-1] != b[i-1]:
				change = change + 1
			current[j] = min(add, delete, change)
			
	return current[n]

# ---- scoring -----
def add_user_score(user,mode,score):
	"""Adds to users score, mode is single or pvp.
		Returns the score for transcription and total user score.
	"""
	total = 0
	score_user = Score.objects.filter(user = user)
	if score_user:
		score_user = score_user[0]
		if mode == "single":
			score_user.score += score
			total = score_user.score
		elif mode =="pvp":
			score_user.pvp += score
			total = score_user.pvp
		else:
			pass
	else:
		score_user = Score()
		score_user.user = user
		if mode == "single":
			score_user.pvp = 0
			score_user.score = score
			total = score_user.score
		elif mode =="pvp":
			score_user.score = 0
			score_user.pvp = score
			total = score_user.pvp
		else:
			pass
	score_user.save()
	return total

THRESHOLD = 3 
def add_transcript_score(word_object,picture,transcript,score):
	"""Add score to transcript, score can have different weight for single or pvp mode.
		When score is > THRESHOLD we mark picture as solved and it is not used in game any more.
	"""
	transcript_object = Transcript.objects.filter(picture = picture, transcript = transcript)
	if transcript_object: 
		transcript_object = transcript_object[0]
		transcript_object.score += score
		if transcript_object.score > THRESHOLD: # word is solved
			word_object.transcript = transcript
			word_object.solved = True
			word_object.save()
		transcript_object.save()
	else:
		transcript_object = Transcript()
		transcript_object.picture = picture
		transcript_object.transcript = transcript
		transcript_object.score = score
		transcript_object.save()

# ---- insert action in database for pvp ----
def insert_action(user,picture,time,transcript):
	action = Action()
	action.user = user
	action.picture = picture
	action.time = time
	action.transcript = transcript
	action.save()

# ---------------------------- page code ----------------------------------

# ---- single player ----
def index(request):
	return render(request,"index.html")

def getpicture(request):
	"""Get nonsolved pricture for transcription."""
	words = Word.objects.filter(solved = False)[:5] # !!!! remove [:5] or change 5 to something way bigger for real game
	sel_word =  words[random.randint(0,len(words)-1)]
	picDict = {}
	picDict["picture"] = sel_word.picture
	return HttpResponse(json.dumps(picDict), content_type="application/json")

SINGLE_SCORE = 1 # weight of single mode transcripts
def sendtranscript(request):
	"""We calculate the score for the user transcript, add it to the users score
		and we add to the transcript score.
	"""
	user = request.POST["user"]
	transcript = request.POST["transcript"]
	picture = request.POST["picture"]
	word_object = Word.objects.get(picture = picture)
	ocr_word = word_object.word
	score = min(len(ocr_word),len(transcript)) - levenshtein(transcript,ocr_word)
	# single game scoring
	total = add_user_score(user,"single",score)
	# transctriptions scoring
	add_transcript_score(word_object,picture,transcript,SINGLE_SCORE)
	result = {}
	result["score"] = score
	result["total"] = total
	return HttpResponse(json.dumps(result), content_type="application/json")
	
# ---- pvp game ----
def pvp(request):
	return render(request,"pvp.html")

def getpvppicture(request):
	"""Get nonsolved oponennt, oponents time and nonsolved picture for pvp game.
		The user can not compete against himself.
	"""
	user = request.POST["user"]
	words = Word.objects.filter(solved = False)[:5] # !!!! remove [:5] or change 5 to something way bigger for real game
	sel_word =  words[random.randint(0,len(words)-1)]
	picture = sel_word.picture
	actions = Action.objects.filter(picture = picture).filter(~Q(user = user))
	sel_action = actions[random.randint(0,len(actions)-1)]
	picDict = {}
	picDict["picture"] = picture
	picDict["oponent"] = sel_action.user
	picDict["time"] = sel_action.time
	return HttpResponse(json.dumps(picDict), content_type="application/json")

PVP_USER_SCORE = 1 # wining pvp score
PVP_SCORE = 1 # weight of pvp mode transcripts
def sendpvptranscript(request):
	user = request.POST["user"]
	oponent = request.POST["oponent"]
	picture = request.POST["picture"]
	transcript = request.POST["transcript"]
	time = int(request.POST["time"])
	word_object = Word.objects.get(picture = picture)
	# get best transcript
	best_transcript = Transcript.objects.filter(picture = picture).order_by("-score")[0].transcript
	# get the Levenshtein distance between user submited transcript and best transcript at the moment
	lev_dis = min(len(best_transcript),len(transcript)) - levenshtein(best_transcript,transcript)
	# get the time that oponent used for transcription
	oponent_time = Action.objects.filter(picture = picture, user = oponent)[0].time
	score = 0
	total = 0
	if lev_dis > 0:
		if time < oponent_time:
			message = "You win!"
			# pvp scoring
			total = add_user_score(user,"pvp",PVP_USER_SCORE)
			# insert transcript to database for pvp game
		else: # lost on time
			message = "You lost - to slow!" 
	else: # lost on accuracy
		message = "You lost - innacurate!" 
	insert_action(user,picture,time,transcript)
	# transctriptions scoring
	add_transcript_score(word_object,picture,transcript,PVP_SCORE)
	result = {}
	result["score"] = score
	result["total"] = total
	result["message"] = message
	return HttpResponse(json.dumps(result), content_type="application/json")

# ---- hi scores ----
def hiscores(request):
	scores = Score.objects.all().order_by("-score")[:20]
	scorespvp = Score.objects.all().order_by("-pvp")[:20]
	return render(request,"hiscores.html",{'scores':scores, 'scorespvp':scorespvp})

# ---- word results ----
def wordresults(request):
	words = Word.objects.filter(solved = True).order_by("picture")[:20]
	return render(request,"wordresults.html",{'words':words})

