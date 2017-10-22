# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.views import generic
from .models import Filter
from django.urls import reverse
from django.template import loader
# Create your views here.
import inspect
from datetime import datetime
from elasticsearch import Elasticsearch
import json
from django.utils.safestring import mark_safe

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import random

#Variables that contains the user credentials to access Twitter API 
access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""



def index(request,results=None,markerCoord=None):
    att=inspect.getmembers(Filter, lambda a:not(inspect.isroutine(a)))
    att=[a[1] for a in att if a[0]=='__dict__'][0]
    attribute_list=[a[len('filter_condition_'):] for a in att if a.startswith('filter_condition_')]
    context_object_name = 'attribute_list'
    template=loader.get_template('mainapp/index.html')
    if results==None:
    	results=[]
    if markerCoord==None:
    	markerCoord=[]
    else:
        markerCoord=str(markerCoord).strip('()')
        markerCoord=markerCoord.split(',')
        markerCoord=[float(l) for l in markerCoord]
    print 'mc=',markerCoord,type(markerCoord)
    try:
        results=json.dumps(results,sort_keys=True, indent=4)
    except:None
    #print results
    context={
    'attribute_list':attribute_list,
    'results':mark_safe(results),
    'markerCoord':mark_safe(markerCoord),
    }
    return HttpResponse(template.render(context, request))	
    
def search(request):
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l,timeout=1.5)

    mapping ="Key_word"
    host='https://search-twitmap-cupqelpnpd3niqdiaprtmmfo7m.us-east-1.es.amazonaws.com'
    es = Elasticsearch([host])
    postForm=request.POST
    search_request={}
    for i in postForm:
        if not (i=='csrfmiddlewaretoken'):
            search_request[i]=postForm[i]
            print i,search_request[i]
    filter=Filter(filter_condition_User=search_request['User'], filter_condition_Hashtag=search_request['Hashtag'],filter_condition_Key_Word=search_request['Key_Word'],submit_time=datetime.now(),submitter=request.META['CSRF_COOKIE'],filter_condition_markerCoord=search_request['markerCoord'])
    print filter
    print 
    mc=filter.filter_condition_markerCoord
    searchBox=mc.strip("()")
    searchBox=searchBox.split(',')
    searchBox=[float(i) for i in searchBox]
    boxSize=1
    searchBox=[searchBox[1]-boxSize,searchBox[0]-boxSize,searchBox[1]+boxSize,searchBox[0]+boxSize]
    print searchBox
    doc = {
        "query": {
            "bool":{
                "should":[
                    {"query_string": {
                        "fields":["user.screen_name","user.name"],
                        "query" : "*"+filter.filter_condition_User+"*" if len(filter.filter_condition_User) else ''
                        }
                    },
                    {"query_string": {
                        "fields":["entities.hashtags.text"],
                        "query" : "*"+str(filter.filter_condition_Hashtag)+"*" if len(str(filter.filter_condition_Hashtag)) else ''
                        }
                    },
                    {"query_string": {
                        "fields":["text"],
                        "query" : "*"+filter.filter_condition_Key_Word+"*" if len(filter.filter_condition_Key_Word) else ''
                        }
                   }
                ]
            }       
        }
    }

    res = es.search(index="tweets", doc_type='tweet', body=doc)
    f=open('log.log','a')
    print >>f, '-------------------Search reuqestion at %s---------------------\n' % str(filter.submit_time)
    global tweets
    tweets=[]
    try:
        stream.filter(locations=searchBox)
    except:
    	None
#    print len(tweets)
    tweets=[json.loads(tweet) for tweet in tweets]
#    for tweet in tweets:
#        print json.dumps(tweet,sort_keys=True, indent=4)

    results=[]
    for hit in tweets:
    	tweet={}
        try:
            tweet["User"]=hit['user']['screen_name']+', '+hit['user']['name']
            tweet["Location"]=hit['user']['location']
            ht={}
            for i in hit['entities']['hashtags']:
            	ht.add(i["text"])
            tweet["Hashtags"]=ht
            tweet["Text"]=hit['text']
            try: 
            	bb=hit['place']['bounding_box']['coordinates'][0]
            	r=random.random()
                lat=(bb[0][0]+bb[1][0]+bb[2][0]+bb[3][0])/len(bb)+(r-0.5)*0.00001
                r=random.random()
                lng=(bb[0][1]+bb[1][1]+bb[2][1]+bb[3][1])/len(bb)+(r-0.5)*0.00001
            except:
            	print 'lat error'
            tweet["Coord"]=str(lat)+','+str(lng)
        except:
        	#print 'info error'
        	None
        filter.save()
       	results.append(tweet)
    f.close()
    return index(request,results,mc)



class StdOutListener(StreamListener):    
    def on_data(self, data):
        tweets.append(data)
        return True
    
    def on_error(self, status):
        print(status)
