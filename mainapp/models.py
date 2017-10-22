# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class Filter(models.Model):
    filter_condition_User=models.CharField(max_length=200)
    filter_condition_Key_Word=models.CharField(max_length=200)
    filter_condition_Hashtag=models.CharField(max_length=200)
    filter_condition_markerCoord=models.CharField(max_length=200)
    submit_time=models.DateTimeField('date published')
    submitter = models.CharField(max_length=200)
    def __str__(self):
    	return 'submitter: '+self.submitter+' time: '+str(self.submit_time)+' User: '+self.filter_condition_User+' Keyword: '+self.filter_condition_Key_Word+' Hashtags: '+self.filter_condition_Hashtag+' markerCoord: '+self.filter_condition_markerCoord
