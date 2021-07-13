from threading import active_count
from django.shortcuts import render, redirect
from django.http import HttpResponse, request, response
import time
from .models import Contest, SiteData, UserData, Profile, Team
from .LCPredictor import getPageNo,getRanklist,fetchAllUserData,getRatingChange,getRatingChangeCached,getForesight
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import json
from datetime import date
from django.contrib import messages
import requests
import string
import random
from .forms import UserRegisterForm,UserProfileForm
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
	return cur,upd,obj2.any_other_headers,obj.foresight_made

def homepage(request):
	predicitions_made,upd,any_other_headers,foresight_made = view_plus(request)
	if any_other_headers=='null':
		any_other_headers=''
	TeamObj = Team.objects.all().order_by('pk')
	upd = upd[::-1]
	return render(request, 'main/home.html',{'members':TeamObj,'foresight_made':foresight_made,'predicitions_made':predicitions_made,'updates':upd,'any_other_headers':any_other_headers})

@login_required
def allcontests(request):
	if request.user.profile.isStaff == True:
		obj = Contest.objects.all()
		obj2 = SiteData.objects.all().first()
		status_data = json.loads(obj2.updates)
		status_data = list(enumerate(status_data))
		status_data = status_data[::-1]
		return render(request, 'main/contests.html',{'status_data':status_data,'data':obj})
	return HttpResponse('Not Allowed')


def predictions(request):
	predicitions_made,upd,any_other_headers,foresight_made = view_plus(request)
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

def status_updates_api(request,apikey,operation):
	obj = SiteData.objects.all().first()
	keys = json.loads(obj.api_keys)
	response = {'status':404,'msg':'Not Allowed'}
	if apikey in keys and request.method == 'POST':
		post_data = json.loads(request.body)
		response = {'status':200,'msg':'API Matched'}
		try:
			data = json.loads(obj.updates)
			if operation == 'CREATE':
				data.append(post_data['data'])
			else:
				del data[int(post_data['index'])]
		except Exception as e:
			print(e)
			response = {'status':505,'msg':'Internal Error'}
			return HttpResponse(json.dumps(response))
		obj.updates = json.dumps(data)
		obj.save()
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
			ranklist = getRanklist(obj.slug,obj.page_limit,obj)
			obj.isRanklist=True
			obj.save()
		# if obj.isUserdata==False:
		# 	userdata = fetchAllUserData(obj.ranklist,obj.title,obj)
		# 	obj.userdata=userdata
		# 	obj.isUserdata=True
		# 	obj.save()
		# if obj.isUserdata and obj.isRanklist and obj.isMeta:
		# 	obj.isPredicted=True
		# 	obj.save()
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
	try:
		data = json.loads(requests.get(f'https://geolocation-db.com/json/{ip}&position=true').content)
		return data['country_name']
	except:
		return "Country API Error"

def add_foresight():
	obj = UserData.objects.all().first()
	obj.foresight_made+=1
	obj.save()

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

@login_required
def dashboard(request):
	if request.user.profile.isStaff == True:
		obj = UserData.objects.all().first()
		page_views = obj.page_views
		foresight_made = obj.foresight_made
		predicitions_made = obj.predicitions_made
		recent_prediction = json.loads(obj.recent_prediction)
		for i in range(len(recent_prediction)):
			recent_prediction[i][0] = int(time.time())-recent_prediction[i][0]
		recent_prediction = recent_prediction[::-1]
		active_users =json.loads(obj.active_users)
		active_users = [[x , active_users[x]] for x in active_users.keys()]
		active_users = sorted(active_users, key=lambda x:x[1],reverse=True)
		active_users=active_users[:20]
		demographics =json.loads(obj.demographics)
		demographics = [[x , demographics[x]] for x in demographics.keys()]
		demographics = sorted(demographics, key=lambda x:x[1],reverse=True)
		demographics=demographics[:20]
		foresights = Profile.objects.all().order_by('-foresights_made')
		
		return render(request,'main/dashboard.html',{'foresights':foresights,'foresight_made':foresight_made,'demographics':demographics,'active_users':active_users,'recent_prediction':recent_prediction,'page_views':page_views,'predicitions_made':predicitions_made,'title':'Dashboard'})
	return HttpResponse("Not Allowed")

@login_required
def foresight_api(request):
	if request.user.profile.isVerified==False:
		return HttpResponse(json.dumps({'status':0, 'data':"Not Allowed : Account Not Verified"}))
	if request.user.profile.isBlacklist==True:
		return HttpResponse(json.dumps({'status':0, 'data':"Not Allowed : Account Blacklisted for multiple unfollows on \"https://github.com/s-i-d-d-i-s\""}))
	last_user_foresight = request.user.profile.last_user_foresight
	time_now = time.time()
	gap = time_now - last_user_foresight
	if gap <= 60:
		return HttpResponse(json.dumps({'status':0, 'data': "Please wait "+str(int(60-gap))+' Seconds'}))
		return HttpResponse("Please wait "+str(60-gap)+' Seconds')
	
	if request.method=='POST':
		data = json.loads(request.body)
		data=data['data']
		rating=data['rating']
		contest_played=data['played']
		res = []
		data = Contest.objects.all().order_by('-pk')
		cnt=5
		for x in data:
			if cnt==0:
				break
			if x.isPredicted==False:
				continue
			temp = int(getForesight(x.ranklist,x.userdata,int(rating),int(contest_played)))
			res.append(f'Rank around <strong class="text-success">{temp}</strong> in {x.title}')
			cnt-=1
		request.user.profile.last_user_foresight = time_now
		request.user.profile.save()
		add_foresight()
		return HttpResponse(json.dumps({'status':1, 'data':res}))
	else:
		return HttpResponse("Not Allowed")
		
@login_required
def foresight(request):
	request.user.profile.foresights_made+=1
	request.user.profile.save()
	return render(request,'main/foresight.html',{'msg':"Know Minimum Rank to get +ve Rating change based on Historic Data",'title':"Foresight"})


def register(request):
	if request.method=='POST':
		form = UserRegisterForm(request.POST)
		profile_form = UserProfileForm(request.POST)
		if form.is_valid() and profile_form.is_valid() :
			github = profile_form.cleaned_data.get('github')
			tmp = len(Profile.objects.filter(github=github).all())
			if tmp!=0:
				messages.warning(request,f"Github Account already being used !")
				return redirect('register')
			user = form.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			profile.save()
			username = form.cleaned_data.get('username')
			messages.success(request,f"Account Created for {username}")
			return redirect('login')
	else:
		form = UserRegisterForm()
		profile_form = UserProfileForm()
	return render(request,'main/register.html',{'form':form,'title':"Register",'profile_form':profile_form})

def generateHash():
	length = 10
	result_str = ''.join(random.choice(string.ascii_uppercase) for i in range(length))
	return result_str

@login_required
def verify_account(request):
	user = request.user
	if user.profile.isVerified:
		return render(request,'main/verify.html',{'title':'Verified','msg':'Your account has been verified!'})
	if user.profile.hashVal=="":
		hashVal = generateHash()
		user.profile.hashVal=hashVal
		user.profile.save()
	hashVal = user.profile.hashVal
	return render(request,'main/verify.html',{'title':'Verify your account','msg':'Please verify your account','hash':hashVal,'account':user.profile.github})

def check_hash(username,hashVal):
	data = json.loads(requests.get(f'https://api.github.com/users/{username}').content)
	return data['name'].strip()==hashVal

@login_required
def verify_account_api(request):
	user = request.user
	if user.profile.isVerified:
		return HttpResponse(json.dumps({'status':1}))
	hashVal = user.profile.hashVal
	github = user.profile.github
	last_verify = user.profile.last_tried_verify
	time_now = time.time()
	gap = time_now - last_verify
	print(gap)
	if gap >= 5*60:
		if check_hash(user.profile.github,hashVal) == False:
			user.profile.last_tried_verify = time_now
			user.profile.save()
			return HttpResponse(json.dumps({'status':0}))
		user.profile.last_tried_verify = time_now
		user.profile.isVerified=True
		user.profile.save()
		return HttpResponse(json.dumps({'status':1}))

	return HttpResponse(json.dumps({'status':3,'time':int(gap)}) )
