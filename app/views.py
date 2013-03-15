import datetime
import hashlib
from pygeoip import GeoIP, GeoIPError
from random import choice, randint
import re
import socket
import sys
import threading
sys.path.append('app/scripts')
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core import serializers
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader, RequestContext
from django.utils import simplejson, timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from models import *

geoip_city_dat = 'GeoIP/GeoLiteCity.dat'
geoip_org_dat = ''

gic = GeoIP(geoip_city_dat)
gio = None
if geoip_org_dat != '':
    gio = GeoIp(geoip_org_dat)

# set socket default timeout to 5 seconds.
# this setting is used by the reverse-DNS lookup
if hasattr(socket, 'setdefaulttimeout'):
    socket.setdefaulttimeout(5)

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
            'error_message': "The account you are trying ot use has been disabled.<br/>" + 
            "Please contact a system administrator.",
        }, context_instance = RequestContext(request))
    # Valid login, active user
    else:
        login(request, user)
        return HttpResponseRedirect('/log/')

def ajax_getCountryInfo(request, _days="0"):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per country.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.
    '--' represents "Unknown"

    format is ["country code", counts]
    eg: { 
            "aaData": [
                ["US", 5],
                ["--", 2],
                ["GB", 1]
            ]
        }
    '''
    days = int(_days) # django passes _days as a string. make it an int
    results = {}
    
    if days == 0:
        countryLog = LogEvent.objects.values('netInfo__country').annotate(count=Count('netInfo__country'))
    else:
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        countryLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('netInfo__country').annotate(count=Count('netInfo__country'))
        
    # convert to JSON
    json_results = []
    for country in countryLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(country['netInfo__country'])
        temp.append(country['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "aaData": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")

def ajax_getDomainInfo(request, _days="0"):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per domain.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["domain", counts]
    eg: { 
            "aaData": [
                ["llnl.gov", 5],
                ["example.com", 2],
                ["Unknown", 1]
            ]
        }
    '''
    days = int(_days) # django passes _days as a string. make it an int
    results = {}
    
    if days == 0:
        domainLog = LogEvent.objects.values('netInfo__domain').annotate(count=Count('netInfo__domain'))
    else:
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        domainLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('netInfo__domain').annotate(count=Count('netInfo__domain'))
        
    # convert to JSON
    json_results = []
    for domain in domainLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(domain['netInfo__domain'])
        temp.append(domain['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "aaData": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")
    
def ajax_getPlatformInfo(request, _days="0"):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per platform.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["platform", counts]
    eg: { 
            "aaData": [
                ["Linux", 5],
                ["Windows", 2],
                ["Darwin", 1]
            ]
        }
    '''
    days = int(_days) # django passes _days as a string. make it an int
    results = {}
    
    if days == 0:
        platformLog = LogEvent.objects.values('machine__platform').annotate(count=Count('machine__platform'))
    else:
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        platformLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('machine__platform').annotate(count=Count('machine__platform'))
        
    # convert to JSON
    json_results = []
    for platform in platformLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(platform['machine__platform'])
        temp.append(platform['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "aaData": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")
    
def ajax_getDetailedPlatformInfo(request, _days="0"):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per platform.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["platform", "version", counts]
    eg: { 
            "aaData": [
                ["Linux", "2.6.32-358.el6.x86_64", 7],
                ["OpenSolaris", "4.0.11", 2],
                ["Windows", "7 x64 SP1", 1],
                ["AIX", "3.0.15", 1]
            ]
        }
    '''
    days = int(_days) # django passes _days as a string. make it an int
    results = {}
    
    if days == 0:
        platformLog = LogEvent.objects.values('machine__platform').annotate(count=Count('machine__platform'))
    else:
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
    json_results = '{ "aaData": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")


def ajax_getSourceInfo(request, _days="0"):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per source.
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["source name", counts]
    eg: { 
            "aaData": [
                ["UV-CDAT", 5],
                ["CDAT", 2],
                ["Build", 1]
            ]
        }
    '''
    days = int(_days) # django passes _days as a string. make it an int
    results = {}
    
    if days == 0:
        domainLog = LogEvent.objects.values('source__name').annotate(count=Count('source__name'))
    else:
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        domainLog = LogEvent.objects.filter(date__range = (date_from, timezone.now())).values('source__name').annotate(count=Count('source__name'))
        
    # convert to JSON
    json_results = []
    for source in domainLog:
        temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
        temp.append(source['source__name'])
        temp.append(source['count'])
        json_results.append(temp)
    json_results = simplejson.dumps(json_results)
    json_results = '{ "aaData": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")

def ajax_getSourceDetailedInfo(request, _days="0"):
    '''
    Returns JSON array of JSON arrays representing the total number of log events per source (by version).
    The optional prameter "_days" specifies how many days back the log should go.
    0 days returns the results for all-time.

    format is ["source name", "source version", counts]
    eg: { 
            "aaData": [
                ["debugPage", "1.0.1rc2", 2],
                ["UV-CDAT", "6.9", 1],
                ["CDAT", "", 3],
            ]
        }
    '''
    days = int(_days) # django passes _days as a string. make it an int
    results = {}
    
    if days == 0:
        domainLog = LogEvent.objects.values('source__name', 'source__version').annotate(count=Count('source__name'))
    else:
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
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
    json_results = '{ "aaData": ' + json_results + '}'
    
    return HttpResponse(json_results, content_type="application/json")

def ajax_getLogDetails(request):
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
            "aaData": 
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
            r['country'] = l['netInfo__country']
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
        json_results = '{ "aaData":' + json_results + '}'
        return HttpResponse(json_results, content_type="application/json")
    else:
        return HttpResponse('Unauthenticated')

def showdebug(request):
    '''
    For debugging use only, will show a form where you can submit log events.
    '''
    if settings.DEBUG:
        return render_to_response('debug.html', {
        }, context_instance = RequestContext(request))
    else:
        raise Http404

def showdebugerr(request):
    '''
    For debugging use only, will show a form where you can submit errors to be logged.
    '''
    if settings.DEBUG:
        return render_to_response('debugerr.html', {
        }, context_instance = RequestContext(request))
    else:
        raise Http404

def showlog(request):
    '''
    Renders the logs.
    '''
    return render_to_response('showlog.html', {
    }, context_instance = RequestContext(request))

# exempt insertlog from CSRF protection, or programs will not be able to submit their statistics!
@csrf_exempt
def insertlog(request, returnLogObject=False):
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
    except Exception, err:
        netInfo_obj = NetInfo()
        # GeoIP stuff (tested with IPv4 only!)
        try:
            geoIpInfo = gic.record_by_addr(uncensored_ip)
            netInfo_obj.country = geoIpInfo['country_code']
            netInfo_obj.latitude = geoIpInfo['latitude']
            netInfo_obj.longitude = geoIpInfo['longitude']
        except (GeoIPError, KeyError) as e:
            netInfo_obj.country = '--'
            netInfo_obj.latitude = ''
            netInfo_obj.longitude = ''
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
    except:
        machine_obj = Machine()
        machine_obj.hashed_hostname = hostname
        machine_obj.platform = platform
        machine_obj.platform_version = platform_version
        machine_obj.save()

    ####### USER #######
    try:
        user_obj = User.objects.get(hashed_username = username)
    except:
        user_obj = User()
        user_obj.hashed_username = username
        user_obj.save()

    ####### SOURCE #######
    try:
        source_obj = Source.objects.get(name = source, version = source_version)
    except:
        source_obj = Source()
        source_obj.name = source
        source_obj.version = source_version
        source_obj.save()

    ####### ACTION #######
    try:
        action_obj = Action.objects.get(name = action)
    except:
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

    if returnLogObject:
        return log
    else:
        return HttpResponse('Thank you for participating!')

# exempt logError from CSRF protection, or programs will not be able to submit their statistics!
@csrf_exempt
def logError(request):
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
        request.POST['action'] = "Error (%s)" % severity
        log_obj = insertlog(request, returnLogObject=True)

        # create our Error object and save it
        error = Error()
        error.logEvent = log_obj
        error.description = description
        error.severity = severity
        error.stackTrace = stackTrace
        error.userComments = userComments
        error.executionLog = executionLog
        error.save()

        return HttpResponse('Your crash report has been recorded. Thank you!')

    except Exception as e:
        print e
        return HttpResponse('''
        I'm really sorry about this, but an error occurred while trying to record your error report!<br/>
        I don't really know how this will help you, but the error message reutnred was:<br/>
        '%s' ''' % e.message)

def _censored_reverse_dns(ip):
    '''
    Returns the censored results of a reverse-DNS lookup.
    eg mycomputername.llnl.gov becomes llnl.gov
    '''
    try:
        host = socket.gethostbyaddr(ip)[0]
        m = re.match(r'.+\.(\w+?\.\w+?)$', host)
        return m.group(1)
    except (socket.herror, AttributeError):
        return 'Unknown'

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
            netInfo_obj.latitude = geoIpInfo['latitude']
            netInfo_obj.longitude = geoIpInfo['longitude']
        except (GeoIPError, KeyError) as e:
            netInfo_obj.country = '--'
            netInfo_obj.latitude = None
            netInfo_obj.longitude = None
        if gio != None:
            try:
                netInfo_obj.organization = gio.org_by_addr(uncensored_ip)
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


