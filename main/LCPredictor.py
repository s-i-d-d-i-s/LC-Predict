import requests
import time
import json
import math
import os
import threading

headers = {
	'authority': 'leetcode.com',
	'accept': 'application/json, text/javascript, */*; q=0.01',
	'x-newrelic-id': 'UAQDVFVRGwEAXVlbBAg=',
	'x-requested-with': 'XMLHttpRequest',
	'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
	'content-type': 'application/json',
	'sec-gpc': '1',
	'sec-fetch-site': 'same-origin',
	'sec-fetch-mode': 'cors',
	'sec-fetch-dest': 'empty',
	'accept-language': 'en-US,en;q=0.9',
	'cookie': 'csrftoken=SYt4auAHmprCYhMeGDZwbnE0hWoSLKRLHb0A7mMpbvoAEPvjYcIdL5LtaWhQJv6B; __cfduid=dc8614cf2c524abada1e54cfa8e118d271619065816; __cf_bm=08dec7596eec629845d4f3f39086483d491e2c40-1619324757-1800-AYKgjE4h5oPn/k7bslI317JZOCKGqrKvRQEJSKFM8EyY57yFeDgrM0KTqzs/c5RUfzN8A7VceydacsvxJjrmrp4=',
}


def getPageNo(contest_slug):
	params = (
		('pagination', '1'),
		('region', 'global'),
	)
	data = json.loads(requests.get('https://leetcode.com/contest/api/ranking/{}/'.format(contest_slug), headers=headers, params=params).content)
	return int(math.ceil(data['user_num']/25))

def getPage(page,data2,visit,PAGE_LIMIT,CONTEST):
	if page > PAGE_LIMIT:
		return
	if page in visit:
		return
	params = (
		('pagination', str(page)),
		('region', 'global'),
	)
	try:
		data = json.loads(requests.get('https://leetcode.com/contest/api/ranking/{}/'.format(CONTEST), headers=headers, params=params).content)
	except:
		print("error at page",page)
		return 
	res = []
	for x in data['total_rank']:
		if int(x['score']) ==0:
			continue
		if x['data_region'] == 'CN':
			res.append([x['rank'],x['username'],1])
		else:
			res.append([x['rank'],x['username'],0])
	data2.extend(res)
	visit.add(page)
	return

def getRanklist(contest,PAGE_LIMIT):
	res = []
	visit=set()
	for i in range(1,1000,50):
		THREADS = []
		for j in range(i,i+50):
			THREADS.append(threading.Thread(target=getPage, args=(j,res,visit,PAGE_LIMIT,contest,)))
		for j in range(len(THREADS)):
			THREADS[j].start()
		for j in range(len(THREADS)):
			THREADS[j].join()
		print(f'{i}')
	res = sorted(res, key=lambda x: x[0])
	res = json.dumps(res)
	return res

def getUserData_US(username,get_current,CONTEST_NAME):
	data = '{"operationName":"getContestRankingData","variables":{"username":\"'+username+'\"},"query":"query getContestRankingData($username: String!) {\\n  userContestRanking(username: $username) {\\n    attendedContestsCount\\n    rating\\n    globalRanking\\n    __typename\\n  }\\n  userContestRankingHistory(username: $username) {\\n    contest {\\n      title\\n      startTime\\n      __typename\\n    }\\n    rating\\n    ranking\\n    __typename\\n  }\\n}\\n"}'
	response = requests.post('https://leetcode.com/graphql', headers=headers, data=data).content
	data = json.loads(response)
	allContests = data['data']['userContestRankingHistory']
	user_k=0
	user_rating=1500
	for x in allContests:
		name = x['contest']['title']
		ranking = x['ranking']
		rating = x['rating']
		if get_current==False and name == CONTEST_NAME:
			break
		user_rating = rating
		if ranking!=0:
			user_k+=1
	return (user_rating,user_k)

def getUserData_CN(username,get_current,CONTEST):
	data = '{"operationName":"userContest","variables":{"userSlug":\"'+username+'\"},"query":"query userContest($userSlug: String!) {\\n  userContestRanking(userSlug: $userSlug) {\\n    currentRatingRanking\\n    ratingHistory\\n    levelHistory\\n    contestRankingHistoryV2\\n contestHistory\\n    __typename\\n  }\\n  globalRatingRanking(userSlug: $userSlug)\\n  userContestScore(userSlug: $userSlug)\\n  contestUnratedContests\\n}\\n"}'
	response = requests.post('https://leetcode-cn.com/graphql', headers=headers, data=data).content
	data = json.loads(response)
	allContests = [x['title_slug'] for x in json.loads(data['data']['userContestRanking']['contestHistory'])]
	allRating = json.loads(data['data']['userContestRanking']['ratingHistory'])
	user_k=0
	user_rating=1500
	for i in range(len(allContests)):
		name = allContests[i]
		rating = allRating[i]
		if get_current==False and  name == CONTEST:
			break
		user_rating = rating
		if rating!=None:
			user_k+=1
	return (user_rating,user_k)

def getUserData(row,CONTEST_NAME,userdata,cache):
	username=row[1]
	fromCN = row[2]
	if username in cache:
		print("Using Cache")
		try:
			userdata[username]=(cache[username][0],cache[username][1])
			return
		except:
			pass
	if username in userdata:
		return 
	if fromCN == 1:
		try:
			cur  = getUserData_CN(username,False,CONTEST_NAME)
			userdata[username]=cur
		except:
			pass
		return
	try:
		cur  = getUserData_US(username,False,CONTEST_NAME)
		userdata[username]=cur
	except:
		try:
			cur  = getUserData_CN(username,False,CONTEST_NAME)
			userdata[username]=cur
		except:
			pass

def fetchAllUserData(ranklist,CONTEST_NAME,obj):
	cac = obj.reference
	cac = json.loads(cac)
	print(type(cac))
	
	ranklist = json.loads(ranklist)
	lssize = len(ranklist)
	cur = obj.userdata
	userData = {}
	if cur != 'null':
		userData = json.loads(cur)
	st = obj.userdata_begin
	for i in range(st,lssize,20):
		THREADS = []
		for j in range(i,i+20):
			if j>=lssize:
				break
			THREADS.append(threading.Thread(target=getUserData, args=(ranklist[j],CONTEST_NAME,userData,cac,)))
		for j in range(len(THREADS)):
			THREADS[j].start()
		for j in range(len(THREADS)):
			THREADS[j].join()
		obj.userdata = json.dumps(userData)
		obj.userdata_progress = f"{i+20}/{lssize}"
		obj.userdata_progress = f"{i+20}/{lssize}"
		obj.userdata_begin=i+20
		obj.save()
		print(f"Done : {i}/{lssize}")
	userData = json.dumps(userData)
	return userData




def getRatingChange(username,ranklist,userData):
	def E(a,b):
		return 1/(1+math.pow(10,(b-a)/400))
	
	def getActualRank(username):
		for i in range(len(ranklist)):
			if ranklist[i][1]==username:
				return i+1
		return None

	def getERank(username,ranklist,userData):
		ans = 1
		for i in range(len(ranklist)):
			if ranklist[i][1]!=username:
				try:
					ans+= ( (E(userData[ranklist[i][1]][0],userData[username][0])) )
				except:
					pass
		return ans
	
	def getMi(Erank,Rank):
		return math.sqrt(Rank*Erank)
	
	def checkBS(Erating):
		ans = 1
		for i in range(len(ranklist)):
			try:
				ans+= ( (E(userData[ranklist[i][1]][0],Erating)) )
			except:
				pass
		return ans
	
	def getErating(rating,m):
		l=1
		r=100000
		while r-l > 0.1:
			mid = (l+r)/2
			cur = checkBS(mid)
			if cur>m:
				l=mid
			else:
				r=mid
		return l
	
	def f(k):
		if k==1:
			return 0.5
		return 2/9
	
	def getDelta(Erating,rating,k):
		try:
			return f(k)*(Erating-rating)
		except:
			return None
	try:

		ranklist = json.loads(ranklist)
		userData = json.loads(userData)
		ret_data={}
		ERank = getERank(username,ranklist,userData)
		ret_data['ERank']= ERank
		ar = getActualRank(username)

		mi = getMi(ERank,ar)
		ret_data['GM']= mi
		ERating = getErating(userData[username][0],mi)
		ret_data['ERating']= ERating
		delta = getDelta(ERating,userData[username][0],userData[username][1])
		ret_data['Delta']= delta
		newrating = userData[username][0] + delta
		ret_data['NewRating']= newrating
		ret_data['nature']=True
		if delta <0:
			ret_data['nature']=False
		return ret_data
	except Exception as e:
		print(e)
		return None

def getCache(username,ranklist,userData,temp_Userdata,res):
	try:
		res[username]=[getRatingChange(username,ranklist,userData)['NewRating'],temp_Userdata[username][1]+1]
	except Exception as e:
		print("Error in getCache",e)
		res[username]=None
		pass

def getRatingChangeCached(ranklist,userData):
	res = {}
	temp_ranklist = json.loads(ranklist)
	temp_Userdata = json.loads(userData)
	ranklist_size = len(temp_ranklist)
	
	for i in range(0,ranklist_size,50):
		THREADS = []
		for j in range(i,i+50):
			if j>=ranklist_size:
				break
			THREADS.append(threading.Thread(target=getCache, args=(temp_ranklist[j][1],ranklist,userData,temp_Userdata,res,)))        
		for j in range(len(THREADS)):
			THREADS[j].start()
		for j in range(len(THREADS)):
			THREADS[j].join()
		print(f"{i+50}/{ranklist_size}")
	return res