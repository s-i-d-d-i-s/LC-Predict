from django.db import models

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
	userdata_begin = models.IntegerField(default=0)
	userdata_progress = models.TextField(default="null")
	reference = models.TextField(default="null")
	def __str__(self):
		return "{} : {}".format(self.title,self.isPredicted)

class SiteData(models.Model):
	page_views = models.IntegerField(default=0)
	predicitions_made = models.IntegerField(default=0)
	recent_prediction = models.TextField(default="[]")
	api_keys = models.TextField(default="[]")
	updates =  models.TextField(default="[]")