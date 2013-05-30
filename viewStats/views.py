import datetime
import hashlib
from pygeoip import GeoIP, GeoIPError
from random import choice, randint
import os
import re
import socket
import sys
import threading
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader, RequestContext
from django.utils import simplejson, timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from usageModel.models import *
from django.conf import settings
if not settings.configured:
    settings.configure()



####### TEMPLATE RENDERERS #######
def show_sign_in_page(request):
    '''
    Shows login page.
    '''
    try:
        username = request.POST['username']
        password = request.POST['password']
    except:
        return render_to_response('authentication_page.html', {
        }, context_instance = RequestContext(request))

    # try logging in
    user = authenticate(username = username, password = password)

    # Invalid login
    if user is None:
        return render_to_response('authentication_page.html', {
            'error_message': "Invalid username or password. Please try again.",
        }, context_instance = RequestContext(request))
    # De-activated user
    elif not user.is_active:
        return render_to_response('authentication_page.html', {
            'error_message': "The account you are trying to use has been disabled.<br/>" + 
            "Please contact a system administrator.",
        }, context_instance = RequestContext(request))
    # Valid login, active user
    else:
        login(request, user)
        return HttpResponseRedirect('../')



def show_log(request):
    '''
    Renders the logs.
    '''
    return render_to_response('showlog.html', {
    }, context_instance = RequestContext(request))



def show_error_log(request):
    '''
    Renders the logs.
    '''
    return render_to_response('showerrorlog.html', {
    }, context_instance = RequestContext(request))



def show_error_details(request, error_id):
    '''
    Renders the template which shows detailed error info.
    '''
    error_obj = get_object_or_404(Error, pk=error_id)
    # countryLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('netInfo__country').annotate(count=Count('netInfo__country'))
    actions = LogEvent.objects.values('date', 'action__name').filter(date__lte=error_obj.date, user=error_obj.logEvent.user, machine=error_obj.logEvent.machine).order_by('-date')[:10]
    for action in actions:
        action['name'] = action['action__name']
        del(action['action__name'])
        
    return render_to_response('errordetails.html', {
        "id": error_id,
        "description": error_obj.description,
        "stack_trace": error_obj.stackTrace,
        "severity": error_obj.severity,
        "user_comments": error_obj.userComments,
        "execution_log": error_obj.executionLog,
        "date": error_obj.date,
        "source": error_obj.logEvent.source,
        "platform": error_obj.logEvent.machine.getPlatform(),
        "actions": actions,
    }, context_instance = RequestContext(request))



def show_debug(request):
    '''
    For debugging use only, will show a form where you can submit log events.
    '''
    if settings.DEBUG:
        return render_to_response('debug.html', {
        }, context_instance = RequestContext(request))
    else:
        raise Http404



def show_debug_error(request):
    '''
    For debugging use only, will show a form where you can submit errors to be logged.
    '''
    if settings.DEBUG:
        return render_to_response('debugerr.html', {
        }, context_instance = RequestContext(request))
    else:
        raise Http404
    


####### AJAX DATA ACCESS #######
def ajax_getCountryInfo(request):
    '''
    Returns JSON array of JSON arrays representing the total number of unique
    machines broken down by country.
    '--' represents "Unknown"

    format is ["country code", counts]
    eg: { 
            "countries": [
                ["US", 5],
                ["--", 2],
                ["GB", 1]
            ]
        }
    '''
    days = int(request.GET.get('days', '0'))
    results = {}
    
    if days == 0:
        countryLog = LogEvent.objects.values('netInfo__country').annotate(count=Count('machine__hashed_hostname', distinct=True))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days)).strftime("%Y-%m-%d")
        countryLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('netInfo__country').annotate(count=Count('machine__hashed_hostname', distinct=True))
        
    # convert to JSON
    json_results = []
    for country in countryLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(country['netInfo__country'])
        temp.append(country['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "countries": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")



def ajax_getDomainInfo(request):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per domain.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["domain", counts]
    eg: { 
            "domains": [
                ["llnl.gov", 5],
                ["example.com", 2],
                ["Unknown", 1]
            ]
        }
    '''
    days = int(request.GET.get('days', '0'))
    results = {}
    
    if days == 0:
        domainLog = LogEvent.objects.values('netInfo__domain').annotate(count=Count('netInfo__domain'))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days)).strftime("%Y-%m-%d")
        domainLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('netInfo__domain').annotate(count=Count('netInfo__domain'))
        
    # convert to JSON
    json_results = []
    for domain in domainLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(domain['netInfo__domain'])
        temp.append(domain['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "domains": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")
   


def ajax_getPlatformInfo(request):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per platform.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["platform", counts]
    eg: { 
            "platforms": [
                ["Linux", 5],
                ["Windows", 2],
                ["Darwin", 1]
            ]
        }
    '''
    days = int(request.GET.get('days', '0'))
    results = {}
    
    if days == 0:
        platformLog = LogEvent.objects.values('machine__platform').annotate(count=Count('machine__platform'))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days)).strftime("%Y-%m-%d")
        platformLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('machine__platform').annotate(count=Count('machine__platform'))
        
    # convert to JSON
    json_results = []
    for platform in platformLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(platform['machine__platform'])
        temp.append(platform['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "platforms": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")
    


def ajax_getDetailedPlatformInfo(request):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per platform.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["platform", "version", counts]
    eg: { 
            "detailedPlatforms": [
                ["Linux", "2.6.32-358.el6.x86_64", 7],
                ["OpenSolaris", "4.0.11", 2],
                ["Windows", "7 x64 SP1", 1],
                ["AIX", "3.0.15", 1]
            ]
        }
    '''
    days = int(request.GET.get('days', '0'))
    results = {}
    
    if days == 0:
        platformLog = LogEvent.objects.values('machine__platform', 'machine__platform_version').annotate(count=Count('machine__platform'))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days)).strftime("%Y-%m-%d")
        platformLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('machine__platform', 'machine__platform_version').annotate(count=Count('machine__platform'))
        
    # convert to JSON
    json_results = []
    for platform in platformLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(platform['machine__platform'])
        temp.append(platform['machine__platform_version'])
        temp.append(platform['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "detailedPlatforms": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")



def ajax_getSourceInfo(request):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per source.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["source name", counts]
    eg: { 
            "sources": [
                ["UV-CDAT", 5],
                ["CDAT", 2],
                ["Build", 1]
            ]
        }
    '''
    days = int(request.GET.get('days', '0'))
    results = {}
    
    if days == 0:
        domainLog = LogEvent.objects.values('source__name').annotate(count=Count('source__name'))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days)).strftime("%Y-%m-%d")
        domainLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('source__name').annotate(count=Count('source__name'))
        
    # convert to JSON
    json_results = []
    for source in domainLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(source['source__name'])
        temp.append(source['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "sources": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")



def ajax_getDetailedSourceInfo(request):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per source (by version).
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["source name", "source version", counts]
    eg: { 
            "detailedSources": [
                ["debugPage", "1.0.1rc2", 2],
                ["UV-CDAT", "6.9", 1],
                ["CDAT", "", 3],
            ]
        }
    '''
    days = int(request.GET.get('days', '0'))
    results = {}
    
    if days == 0:
        domainLog = LogEvent.objects.values('source__name', 'source__version').annotate(count=Count('source__name'))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days)).strftime("%Y-%m-%d")
        domainLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('source__name', 'source__version').annotate(count=Count('source__name'))
        
    # convert to JSON
    json_results = []
    for source in domainLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(source['source__name'])
        temp.append(source['source__version'])
        temp.append(source['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "detailedSources": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")



def ajax_getLogEventList(request):
    '''
    Returns JSON array of JSON objects representing the 200 most recent log events.
    Requires log-in to access, because the combination of Domain and Action is too personally identifyable.
    The information available is:
        domain
        source
        country
        platform
        date
        action

    eg: { 
            "logs": 
            [
                {   
                    "domain": "llnl.gov", 
                    "source": "debugPage v1.0.1rc2", 
                    "country": "US", 
                    "platform": "Windows v7 x64 SP1", 
                    "date": "2013-03-14 16:58:21", 
                    "action": "Started UV-CDAT"
                }, 
                {   
                    "domain": "llnl.gov", 
                    "source": "debugPage v1.0.1rc2", 
                    "country": "US", 
                    "platform": "Windows v7 x64 SP1", 
                    "date": "2013-03-14 16:57:04", 
                    "action": "Error (FATAL)"
                }
            ]
        }
    '''
    if request.user.is_authenticated():
        # get the most recent 200 log events
        logs = LogEvent.objects.all().order_by('-date')[:200].values('date',
                                                                    'machine__platform',
                                                                    'machine__platform_version',
                                                                    'netInfo__country',
                                                                    'netInfo__city',
                                                                    'netInfo__domain',
                                                                    'source__name',
                                                                    'source__version',
                                                                    'action__name')
        results = []
        for l in logs:
            # create a dictionary for each record. Resulting JSON will look like [{"A": B}, {"C": D}]
            # this will allow DataTables to show information in an order-independent manner, making it easy to extend later
            r = {}
            r['date'] = l['date'].strftime("%Y-%m-%d %H:%M:%S")
            r['platform'] = l['machine__platform']
            r['location'] = "%s, %s" % (l['netInfo__city'], l['netInfo__country'])
            r['domain'] = l['netInfo__domain']
            r['source'] = l['source__name']
            r['action'] = l['action__name']
            
            # add version numbers for source and action if there is one
            if l['machine__platform_version'] != None and l['machine__platform_version'] != "":
                r['platform'] += " v" + l['machine__platform_version']
            if l['source__version'] != None and l['source__version'] != "":
                r['source'] += " v" + l['source__version']
                
            results.append(r)
        
        # convert to JSON
        json_results = simplejson.dumps(results)
        json_results = '{ "logs":' + json_results + '}'
        return HttpResponse(json_results, content_type="application/json")
    else:
        return HttpResponse('Unauthenticated')



def ajax_getErrorList(request):
    '''
    Returns JSON array of JSON objects representing the 100 most recent errors.
    Requires log-in to access, because the information is too personally identifyable.
    The information available is:
        domain
        source
        city, country
        platform
        date
        error description
        error severity
    '''
    if request.user.is_authenticated():
        # get the most recent 200 log events
        logs = Error.objects.all().order_by('-date')[:100].values('id',
                                                                    'date',
                                                                    'logEvent__machine__platform',
                                                                    'logEvent__machine__platform_version',
                                                                    'logEvent__netInfo__country',
                                                                    'logEvent__netInfo__city',
                                                                    'logEvent__netInfo__domain',
                                                                    'logEvent__source__name',
                                                                    'logEvent__source__version',
                                                                    'description',
                                                                    'severity',
                                                                    'stackTrace',
                                                                    'userComments',
                                                                    'executionLog',)
        results = []
        for l in logs:
            # create a dictionary for each record. Resulting JSON will look like [{"A": B}, {"C": D}]
            # this will allow DataTables to show information in an order-independent manner, making it easy to extend later
            r = {}
            r['id'] = l['id']
            r['date'] = l['date'].strftime("%Y-%m-%d %H:%M:%S")
            r['platform'] = l['logEvent__machine__platform']
            r['location'] = "%s, %s" % (l['logEvent__netInfo__city'], l['logEvent__netInfo__country'])
            r['domain'] = l['logEvent__netInfo__domain']
            r['source'] = l['logEvent__source__name']
            r['description'] = l['description']
            r['severity'] = l['severity']
            r['stacktrace'] = l['stackTrace']
            r['usercomments'] = l['userComments']
            r['executionlog'] = l['executionLog']
            
            # add version numbers for source and action if there is one
            if l['logEvent__machine__platform_version'] != None and l['logEvent__machine__platform_version'] != "":
                r['platform'] += " v" + l['logEvent__machine__platform_version']
            if l['logEvent__source__version'] != None and l['logEvent__source__version'] != "":
                r['source'] += " v" + l['logEvent__source__version']
                
            results.append(r)
        
        # convert to JSON
        json_results = simplejson.dumps(results)
        json_results = '{ "errors":' + json_results + '}'
        return HttpResponse(json_results, content_type="application/json")
    else:
        return HttpResponse('Unauthenticated')