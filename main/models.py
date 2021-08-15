from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Contest(models.Model):
	title = models.CharField(max_length=30, default="Untitled")
	slug = models.CharField(max_length=30, default="Untitled")
	page_limit = models.IntegerField(default=-1)
	isMeta = models.BooleanField(default=False)
	isPredicted = models.BooleanField(default=False)
	isProcess = models.IntegerField(default=0)
	isRanklist = models.BooleanField(default=False)
	isUserdata = models.BooleanField(default=False)
	ranklist = models.TextField(default="null")
	userdata = models.TextField(default="null")
	userdata_progress = models.TextField(default="null")
	manager = models.CharField(max_length=30,default='null')
	def __str__(self):
		return "{} : {}".format(self.title,self.isPredicted)

class SiteData(models.Model):
	any_other_headers = models.TextField(default="null")
	updates =  models.TextField(default="[]")
	def __str__(self):
		return "PK : {}".format(self.pk)

class UserData(models.Model):
	page_views = models.IntegerField(default=0)
	recent_prediction = models.TextField(default="[]")
	demographics =  models.TextField(default="{}")
	predicitions_made = models.IntegerField(default=0)
	foresight_made = models.IntegerField(default=0)
	active_users = models.TextField(default="{}")
	predictions_heatmap = models.TextField(default="{}")
	def __str__(self):
		return "Views : {}".format(self.page_views)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	github = models.CharField(max_length=30)
	apikey = models.CharField(max_length=30,default='null')
	isStaff = models.BooleanField(default=False)
	isVerified = models.BooleanField(default=False)
	last_tried_verify = models.IntegerField(default=0)
	hashVal = models.CharField(max_length=25,default="")
	last_user_foresight = models.IntegerField(default=0)
	foresights_made = models.IntegerField(default=0)
	violations = models.IntegerField(default=0)
	isBlacklist = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.user.username} Profile'

class Team(models.Model):
	username = models.CharField(max_length=30,default='null')
	name = models.CharField(max_length=30,default='null')
	img = models.CharField(max_length=255,default='#')
	work = models.CharField(max_length=255,default='null')
	github = models.CharField(max_length=255,default='null')
	codeforces = models.CharField(max_length=255,default='null')
	leetcode = models.CharField(max_length=255,default='null')
	atcoder = models.CharField(max_length=255,default='null')
	def __str__(self):
		return self.name