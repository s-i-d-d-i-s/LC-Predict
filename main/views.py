from django.shortcuts import render
from .models import Contest, SiteData
from .LCPredictor import getPageNo,getRanklist,fetchAllUserData,getRatingChange,getRatingChangeCached
from django.contrib.auth.decorators import login_required
import json
# Create your views here.

def view_plus():
	obj = SiteData.objects.all().first()
	cur = obj.predicitions_made
	upd = obj.updates
	upd = json.loads(upd)
	obj.page_views+=1
	obj.save()
	return cur,upd

def prediction_plus(username,pk):
	obj = SiteData.objects.all().first()
	obj.page_views+=1
	data = json.loads(obj.recent_prediction)
	data.append(username+'||'+pk)
	while len(data)>10:
		data=data[1:]
	obj.recent_prediction=json.dumps(data)
	obj.predicitions_made+=1
	obj.save()

def homepage(request):
	predicitions_made,upd = view_plus()

	return render(request, 'main/home.html',{'predicitions_made':predicitions_made,'updates':upd})

@login_required
def allcontests(request):
	obj = Contest.objects.all()
	return render(request, 'main/contests.html',{'data':obj})


def status(request):
	view_plus()
	obj = Contest.objects.all().order_by("-pk")
	return render(request, 'main/status.html',{'data':obj,'title':'Status'})

@login_required
def predict_contest(request,pk):
	obj = Contest.objects.filter(pk=pk).first()
	if obj.isPredicted==True:
		return render(request, 'main/showrating.html',{'msg':"Here are your rating changes"})
	else:
		obj.isProcess=True
		obj.save()
		if obj.isMeta==False:
			pages = getPageNo(obj.slug)
			obj.page_limit=pages
			obj.isMeta=True
			obj.save()
		if obj.isRanklist==False:
			ranklist = getRanklist(obj.slug,obj.page_limit)
			obj.ranklist=ranklist
			obj.isRanklist=True
			obj.save()
		if obj.isUserdata==False:
			userdata = fetchAllUserData(obj.ranklist,obj.title,obj)
			obj.userdata=userdata
			obj.isUserdata=True
			obj.save()
		if obj.isUserdata and obj.isRanklist and obj.isMeta:
			obj.isProcess=False
			obj.isPredicted=True
			obj.save()

		return render(request, 'main/showrating.html',{'msg':"Rating Change has been calculated. Please try loading page again"})


@login_required
def cache_contest(request,pk):
	obj = Contest.objects.filter(pk=pk).first()
	if obj.isPredicted==True:
		data = getRatingChangeCached(obj.ranklist,obj.userdata)
		obj.reference=json.dumps(data)
		obj.save()
		return render(request, 'main/showrating.html',{'msg':"Here are your rating changes"})
	else:
		return render(request, 'main/showrating.html',{'msg':"Rating Change has not been calculated. Please try loading page again"})

def predict_user(request,pk,username):
	view_plus()
	prediction_plus(username,pk)
	try:
		obj = Contest.objects.filter(pk=pk).first()
	except:
		return render(request, 'main/showrating.html',{'msg':"Invalid Contest Key"})
	change_data = getRatingChange(username,obj.ranklist,obj.userdata)
	return render(request, 'main/rating_predictions.html',{'data':change_data,'title':obj.title,'username':username})
