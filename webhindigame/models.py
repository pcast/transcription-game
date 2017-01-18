from django.db import models

# picture is a name of a graphical represetation of a word to be transcribed (png file)
# word is the result of OCR program
# transcript - the transcript that crossed the threshold for correct answer 
# solved - every picture starts with solved = False and is set to True when transcript score gets over the threshold 
class Word(models.Model):
	picture = models.CharField(max_length=50, unique=True)
	word = models.CharField(max_length=50)
	transcript = models.CharField(max_length=50)
	solved = models.BooleanField()

# user - unique user
# score - cumulative sigle player score for user 
# pvp - cumulative pvp player score for user 
class Score(models.Model):
	user = models.CharField(max_length=50, unique=True)
	score = models.IntegerField()
	pvp = models.IntegerField()

# picture is a name of a graphical represetation of a word to be transcribed (png file)
# transcript - users transcript of a word
# score - cumulative score for a transcript - one picture can have more then one transcript
class Transcript(models.Model):
	picture = models.CharField(max_length=50)
	transcript = models.CharField(max_length=50)
	score = models.IntegerField()

# user - unique user
# picture is a name of a graphical represetation of a word to be transcribed (png file)
# transcript - users transcript of a word
# time - users time for transcripting the word in miliseconds
class Action(models.Model):
	user = models.CharField(max_length=50)
	picture = models.CharField(max_length=50)
	transcript = models.CharField(max_length=50)
	time = models.IntegerField()
