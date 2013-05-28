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
from models import *
from django.conf import settings
if not settings.configured:
    settings.configure()

geoip_city_dat = settings.GEOLITECITY_ABSOLUTE_PATH
geoip_org_dat = settings.GEOORGANIZATION_ABSOLUTE_PATH

default_sleep_minutes = 30 # default amount of time which must pass before the same event from the same user is logged again

gic = None
try:
    gic = GeoIP(geoip_city_dat)
except IOError,err:
    sys.stderr.write("""
ERROR: Could not find GeoIP database. Tried looking in "%s".
If this is not where you have your GeoIP .dat file stored, edit
GEOLITECITY_ABSOLUTE_PATH in live/local_settings.py\nIf you don't have the
GeoIP City database, you can get it from "http://dev.maxmind.com/geoip/geolite".
""" % (geoip_city_dat))
    sys.exit(1)
gio = None
try:
    gio = GeoIP(geoip_org_dat)
except IOError:
    # we don't want to spam the log with warning messages, so don't do anything here.
    # it's desgined to work without the GeoIP Organization database anyway...
    pass

# set socket default timeout to 5 seconds.
# this setting is used by the reverse-DNS lookup
if hasattr(socket, 'setdefaulttimeout'):
    socket.setdefaulttimeout(5)



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
    Returns JSON array of JSON arrays representing the total number of log events per country.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.
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
        countryLog = LogEvent.objects.values('netInfo__country').annotate(count=Count('netInfo__country'))
    else:
        date_from = (timezone.now() - timezone.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        countryLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('netInfo__country').annotate(count=Count('netInfo__country'))
        
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
        date_from = (timezone.now() - timezone.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
        date_from = (timezone.now() - timezone.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
        date_from = (timezone.now() - timezone.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
        date_from = (timezone.now() - timezone.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
        date_from = (timezone.now() - timezone.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
    
    

# exempt logEvent from CSRF protection, or programs will not be able to submit their statistics!
@csrf_exempt
def log_event(request, returnLogObject=False):
    '''
    Creates a LogEvent.
    '''
    uncensored_ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    # in case we're behind a proxy, get the IP from the HTTP_X_FORWARDED_FOR key instead
    if uncensored_ip == '0.0.0.0' or uncensored_ip == '127.0.0.1':
        uncensored_ip = request.META.get('HTTP_X_FORWARDED_FOR', '0.0.0.0')

    censored_ip = _censor_ip(uncensored_ip)

    domain = request.META.get('REMOTE_HOST', 'Unknown')
    if domain == '' or 'Unknown':
        domain =_censored_reverse_dns(uncensored_ip)

    # if the request is missing some fields, it means someone or something probably just stumbled here by accident, so 404
    try:
        platform = request.POST['platform']
        platform_version = request.POST['platform_version']
        source = request.POST['source']
        source_version = request.POST['source_version']
        action = request.POST['action']
        username = request.POST['hashed_username']
        hostname = request.POST['hashed_hostname']
    except MultiValueDictKeyError as e:
        raise Http404

    ####### NETINFO #######
    try:
        netInfo_obj = NetInfo.objects.get(ip = censored_ip)
    except ObjectDoesNotExist as err:
        netInfo_obj = NetInfo()
        # GeoIP stuff (tested with IPv4 only!)
        try:
            geoIpInfo = gic.record_by_addr(uncensored_ip)
            netInfo_obj.country = geoIpInfo['country_code']
            netInfo_obj.city = geoIpInfo['city']
            if netInfo_obj.city == '':
                netInfo_obj.city = 'Unknown'
            netInfo_obj.latitude = str(geoIpInfo['latitude'])
            netInfo_obj.longitude = str(geoIpInfo['longitude'])
        except (GeoIPError, KeyError, AttributeError) as e:
            netInfo_obj.country = '--'
            netInfo_obj.city = "Unknown"
            netInfo_obj.latitude = 0.0
            netInfo_obj.longitude = 0.0
        if gio != None:
            try:
                netInfo_obj.organization = gio.org_by_addr(uncensored_ip)
            except GeoIPError as e:
                netInfo_obj.organization = 'Unknown'
        netInfo_obj.ip = censored_ip
        netInfo_obj.domain = domain
        netInfo_obj.save()

    ####### MACHINE #######
    try:
        machine_obj = Machine.objects.get(hashed_hostname = hostname)
    except ObjectDoesNotExist as err:
        machine_obj = Machine()
        machine_obj.hashed_hostname = hostname
        machine_obj.platform = platform
        machine_obj.platform_version = platform_version
        machine_obj.save()

    ####### USER #######
    try:
        user_obj = User.objects.get(hashed_username = username)
    except ObjectDoesNotExist as err:
        user_obj = User()
        user_obj.hashed_username = username
        user_obj.save()

    ####### SOURCE #######
    try:
        source_obj = Source.objects.get(name = source, version = source_version)
    except ObjectDoesNotExist as err:
        source_obj = Source()
        source_obj.name = source
        source_obj.version = source_version
        source_obj.save()

    ####### ACTION #######
    try:
        action_obj = Action.objects.get(name = action)
    except ObjectDoesNotExist as err:
        action_obj = Action()
        action_obj.name = action
        action_obj.save()

    ####### CREATE LOG EVENT #######
    # first, check if this user has logged the same event within the last default_sleep_minutes.
    # if they have, ignore this log event.
    try:
        sleepTime = int(request.POST.get('sleep', default_sleep_minutes))
    except ValueError:
        sleepTime = default_sleep_minutes

    # get most recent log event with same user/machine/action/etc
    try:
        prevLogEvent = LogEvent.objects.filter(user = user_obj,
                                               machine = machine_obj,
                                               netInfo = netInfo_obj,
                                               source = source_obj,
                                               action = action_obj).latest('date')
    except ObjectDoesNotExist as e:
        prevLogEvent = None
        
    if sleepTime <= 0 or prevLogEvent == None or prevLogEvent.date < (timezone.now() - timezone.timedelta(minutes=sleepTime)):
        log = LogEvent()
        log.user = user_obj
        log.machine = machine_obj
        log.netInfo = netInfo_obj
        log.source = source_obj
        log.action = action_obj
        try:
            log.save()
            responseMsg = "Thank you for participating!"
        except IntegrityError:
            responseMsg = "Ignoring attempted duplicate log addition."
        
    else:
        log = prevLogEvent
        responseMsg = "I'm ignoring you because you already sent this event within the last %i minutes!" % sleepTime

    if returnLogObject:
        return log
    else:
        return HttpResponse(responseMsg)



# exempt logError from CSRF protection, or programs will not be able to submit their statistics!
@csrf_exempt
def log_error(request):
    '''
    Creates an Error object, which contains information about an error that occurred.
    '''
    try:
        # get info from the POST
        description = request.POST.get('description', 'No description provided.')
        severity = request.POST.get('severity', 'Unknown').upper()
        stackTrace = request.POST.get('stack_trace', '')
        userComments = request.POST.get('comments', '')
        executionLog = request.POST.get('execution_log', '')

        # create a LogEntry with the appropriate action
        request.POST = request.POST.copy() # to make it mutable
        request.POST['sleep'] = 0 # force it to create unique log events for errors.
        request.POST['action'] = "Error (%s) - %s" % (severity, description[:30])
        log_obj = log_event(request, returnLogObject=True)

        # create our Error object and save it
        error = Error()
        error.logEvent = log_obj
        error.description = description
        error.severity = severity
        error.stackTrace = stackTrace
        error.userComments = userComments
        error.executionLog = executionLog
        try:
            error.save()
            return HttpResponse('Your crash report has been recorded. Thank you!')
        except IntegrityError:
            return HttpResponse('Ignoring attempted duplicate error report addition.')



    except Exception as e:
        sys.stderr.write("Fatal Exception in uvcdat usage: " + str(e))
        status_code = 500
        response = render_to_response('error.html', {
            'error_msg': str(e),
            'status_code': status_code
        }, context_instance = RequestContext(request))
        response.status_code = status_code
        return response



def _censored_reverse_dns(ip):
    '''
    Returns the censored results of a reverse-DNS lookup.
    eg mycomputername.llnl.gov becomes llnl.gov
    '''
    try:
        host = socket.gethostbyaddr(ip)[0]
        m = re.match(r'.+\.(\w+?\.\w+?)$', host)
        return m.group(1)
    except (socket.herror, socket.timeout, AttributeError):
        return 'unknown'



def _censor_ip(ip):
    '''
    Returns a censored IPv4 address by zeroing-out the last octet.
    eg 12.34.56.78 --> 12.34.56.0
    '''
    # from beginning of string, matches the first three sets of 1-3 digits separated by a period
    m = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3})', ip) 
    return m.group(1) + ".0"



# fills the DB with randomly generated records
def _fill_db(num_entries_to_add):
    '''
    Logs randomly generated data. Only usable from the command line in debug mode. DO NOT reference this in app/urls.py
    '''
    # if Django's not running  in debug mode, 404 out
    if not settings.DEBUG:
        raise Http404

    i = 0
    while i < num_entries_to_add:
        i += 1
        uncensored_ip = "%s.%s.%s.%s" % (randint(1,255), randint(0, 255), randint(0,255), randint(1,254))
        censored_ip = _censor_ip(uncensored_ip)
        domain = _censored_reverse_dns(uncensored_ip)
        hostname = "testMachine " + str(randint(0, 10000))
        platform = choice(['Linux', 'Windows', 'OSX', 'FreeBSD', 'OpenBSD', 'AIX', 'Solaris', 'OpenSolaris', 'Linux']) # Linux included 2x so it comes-up more frequently
        platform_version = "%s.%s.%s" % (randint(1,4), randint(0,3), randint(0,15))
        username = "user " + str(randint(0, 10000))
        source = choice(['Build', 'CDAT', 'UV-CDAT', 'ESGF'])
        if randint(0,1) == 1:
            source_version = "%s.%s" % (randint(1,8), randint(0,9))
        else:
            source_version = ''
        if source == 'Build':
            action = 'Build'
        else:
            action = choice(['FirstRun', 'Start', 'LoadModule', 'Exit', 'Other thing', 'Something', 'Stuff'])
        
        
        ####### NETINFO #######
        netInfo_obj = NetInfo()
        # GeoIP stuff (tested with IPv4 only!)
        try:
            geoIpInfo = gic.record_by_addr(uncensored_ip)
            netInfo_obj.country = geoIpInfo['country_code']
            netInfo_obj.city = geoIpInfo['city']
            if netInfo_obj.city == '':
                netInfo_obj.city = 'Unknown'
            netInfo_obj.latitude = geoIpInfo['latitude']
            netInfo_obj.longitude = geoIpInfo['longitude']
        except (GeoIPError, KeyError, AttributeError) as e:
            netInfo_obj.country = '--'
            netInfo_obj.city = "Unknown"
            netInfo_obj.latitude = 0.0
            netInfo_obj.longitude = 0.0
        if gio != None:
            try:
                netInfo_obj.organization = gio.org_by_addr(uncensored_ip)
                if netInfo_obj.organization == '':
                    netInfo_obj.organization = 'Unknown'
            except GeoIPError as e:
                netInfo_obj.organization = 'Unknown'
        netInfo_obj.ip = censored_ip
        netInfo_obj.domain = domain
        netInfo_obj.save()
        
        ####### MACHINE #######
        machine_obj = Machine()
        machine_obj.hashed_hostname = hostname
        machine_obj.platform = platform
        machine_obj.platform_version = platform_version
        machine_obj.save()
        
        ####### USER #######
        user_obj = User()
        user_obj.hashed_username = username
        user_obj.save()
    
        ####### SOURCE #######
        source_obj = Source()
        source_obj.name = source
        source_obj.version = source_version
        source_obj.save()
    
        ####### ACTION #######
        action_obj = Action()
        action_obj.name = action
        action_obj.save()
    
        ####### CREATE LOG EVENT #######
        log = LogEvent()
        log.user = user_obj
        log.machine = machine_obj
        log.netInfo = netInfo_obj
        log.source = source_obj
        log.action = action_obj
        log.save()
