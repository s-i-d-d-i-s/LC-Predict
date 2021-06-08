from threading import active_count
from django.shortcuts import render
from django.http import HttpResponse, request, response
import time
from .models import Contest, SiteData, UserData
from .LCPredictor import getPageNo,getRanklist,fetchAllUserData,getRatingChange,getRatingChangeCached
from django.contrib.auth.decorators import login_required
import json
from datetime import date
import requests
# Create your views here.

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def view_plus(request=None):
	
		
	obj = UserData.objects.all().first()
	if request!=None:
		country = getCountry(get_client_ip(request))
		foo = json.loads(obj.demographics)
		print(foo)
		if country in foo.keys():
			foo[country]+=1
		else:
			foo[country]=1
		obj.demographics=json.dumps(foo)

	cur = obj.predicitions_made
	obj2 = SiteData.objects.all().first()
	upd = obj2.updates
	upd = json.loads(upd)
	obj.page_views+=1
	obj.save()
	return cur,upd,obj2.any_other_headers

def homepage(request):
	predicitions_made,upd,any_other_headers = view_plus(request)
	if any_other_headers=='null':
		any_other_headers=''
	return render(request, 'main/home.html',{'predicitions_made':predicitions_made,'updates':upd,'any_other_headers':any_other_headers})

@login_required
def allcontests(request):
	obj = Contest.objects.all()
	return render(request, 'main/contests.html',{'data':obj})


def predictions(request):
	predicitions_made,upd,any_other_headers = view_plus(request)
	if any_other_headers=='null':
		any_other_headers=''
	obj = Contest.objects.all().order_by("-pk")
	return render(request, 'main/status.html',{'data':obj,'title':'Predictions','any_other_headers':any_other_headers})


def predict_contest_api(request,apikey,pk):
	obj = SiteData.objects.all().first()
	keys = json.loads(obj.api_keys)
	response = {'status':404,'msg':'API Key Mismatch'}
	if apikey in keys:
		response = {'status':200,'msg':'API Matched'}
		obj = Contest.objects.filter(pk=pk)
		if len(obj) ==0 :
			response = {'status':404,'msg':'No Such Contest Exists'}
		else:
			obj = obj.first()
			isRunning = int(time.time()) - obj.isProcess
			if isRunning <= 50 :
				response = {'status':404,'msg':'Prediction already running'}
			else:
				obj.isProcess=int(time.time())
				obj.save()
				predict_contest(pk)
	return HttpResponse(json.dumps(response))

def get_contest_status(request,apikey,pk):
	obj = SiteData.objects.all().first()
	keys = json.loads(obj.api_keys)
	response = {'status':404,'msg':'API Key Mismatch'}
	if apikey in keys:
		response = {'status':200,'msg':'API Matched'}
		obj = Contest.objects.filter(pk=pk)
		if len(obj) ==0 :
			response = {'status':404,'msg':'No Such Contest Exists'}
		else:
			obj = obj.first()
			response['page_limit']=obj.page_limit
			response['isMeta']=obj.isMeta
			response['isPredicted']=obj.isPredicted
			response['isProcess']=obj.isProcess
			response['isRanklist']=obj.isRanklist
			response['isUserdata']=obj.isUserdata
			response['userdata_progress']=obj.userdata_progress
	return HttpResponse(json.dumps(response))

def predict_contest(pk):
	obj = Contest.objects.filter(pk=pk).first()
	if obj.isPredicted==True:
		return {'msg':"Here are your rating changes"}
	else:
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
			obj.isPredicted=True
			obj.save()
		return 


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
	view_plus(request)
	try:
		obj = Contest.objects.filter(pk=pk).first()
		if obj.isPredicted==False:
			return render(request, 'main/showrating.html',{'msg':"Prediction not available"})
	except:
		return render(request, 'main/showrating.html',{'msg':"Invalid Contest Key"})
	
	change_data = getRatingChange(username,obj.ranklist,obj.userdata)
	if change_data == None:
		return HttpResponse("User not found !")
	add_prediction(username,obj.title)
	response = change_data
	
		
	return HttpResponse(json.dumps(response))

def getCountry(ip):
	data = json.loads(requests.get(f'https://geolocation-db.com/json/{ip}&position=true').content)
	return data['country_name']

def add_prediction(username,contest):
	obj = UserData.objects.all().first()
	obj.predicitions_made+=1
	data = json.loads(obj.recent_prediction)
	data.append([int(time.time()),username,contest])
	while len(data)>10:
		data=data[1:]
	obj.recent_prediction=json.dumps(data)
	data = json.loads(obj.active_users)
	if username in data:
		data[username]+=1
	else:
		data[username]=1
	obj.active_users=json.dumps(data)
	today = str(date.today())
	data = json.loads(obj.predictions_heatmap)
	if today in data:
		data[today]+=1
	else:
		data[today]=1
	obj.predictions_heatmap=json.dumps(data)
	obj.save()
	
def dashboard(request):
	obj = UserData.objects.all().first()
	page_views = obj.page_views
	predicitions_made = obj.predicitions_made
	recent_prediction = json.loads(obj.recent_prediction)
	for i in range(len(recent_prediction)):
		recent_prediction[i][0] = int(time.time())-recent_prediction[i][0]
	recent_prediction = recent_prediction[::-1]
	active_users =json.loads(obj.active_users)
	active_users = [[x , active_users[x]] for x in active_users.keys()]
	active_users = sorted(active_users, key=lambda x:x[1],reverse=True)
	return render(request,'main/dashboard.html',{'active_users':active_users,'recent_prediction':recent_prediction,'page_views':page_views,'predicitions_made':predicitions_made,'title':'Dashboard'})