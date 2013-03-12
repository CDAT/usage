import datetime
import hashlib
from pygeoip import GeoIP, GeoIPError
from random import choice, randint
import re
import socket
import sys
import threading
sys.path.append('app/scripts')
from django.contrib.auth import authenticate, login
from django.core import serializers
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

if hasattr(socket, 'setdefaulttimeout'):
    socket.setdefaulttimeout(5)

def hello(request):
    return HttpResponse("Hello World")

def show_authentication_page(request):
    return render_to_response('authentication_page.html', {
    }, context_instance=RequestContext(request))

# hit count by country in the last x days
def ajax_getCountryInfo_days(request, _days="0"):
    if request.user.is_authenticated():
        days = int(_days) # django passes _days as a string. make it an int
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        results = {}
        
        if days == 0:
            countryLog = LogEvent.objects.all().values('netInfo__country')
        else:
            countryLog = LogEvent.objects.all().filter(date__range = (date_from, timezone.now())).values('netInfo__country')
        for country in countryLog:
            currentCountryCount = results.get(country['netInfo__country'], 0)
            results[country['netInfo__country']] = currentCountryCount + 1
            
        # convert to JSON
        json_results = []
        for key in results.keys():
            temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
            temp.append(key)
            temp.append(results[key])
            json_results.append(temp)
        json_results = simplejson.dumps(json_results)
        json_results = '{ "aaData": ' + json_results + '}'
        
        return HttpResponse(json_results, content_type="application/json")
    else:
        return HttpResponse("Unauthenticated")

# hit count by domain in the last x days
def ajax_getDomainInfo(request, _days="0"):
    if request.user.is_authenticated():
        days = int(_days) # django passes _days as a string. make it an int
        date_from = (timezone.now() - datetime.timedelta(days = days - 1)).strftime("%Y-%m-%d")
        results = {}
        
        if days == 0:
            domainLog = LogEvent.objects.all().values('netInfo__domain')
        else:
            domainLog = LogEvent.objects.all().filter(date__range = (date_from, timezone.now())).values('netInfo__domain')
        
        for domain in domainLog:
            currentDomainCount = results.get(domain['netInfo__domain'], 0)
            results[domain['netInfo__domain']] = currentDomainCount + 1
            
            
        # convert to JSON
        json_results = []
        for key in results.keys():
            temp = [] # create a list for each pair because DataTables likes input in this style: [["US": 15], ["GB":7]]
            temp.append(key)
            temp.append(results[key])
            json_results.append(temp)
        json_results = simplejson.dumps(json_results)
        json_results = '{ "aaData": ' + json_results + '}'
        
        return HttpResponse(json_results, content_type="application/json")
    else:
        return HttpResponse("Unauthenticated")

def ajax_getLogInfo(request):
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
    return render_to_response('debug.html', {
    }, context_instance = RequestContext(request))

def showlog(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except:
        # Either no username or no password supplied. They tried skipping the login and going
        # straight to the results! Redirect them to the login page
        return HttpResponseRedirect('/log/')

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
        return render_to_response('showlog.html', {
        }, context_instance = RequestContext(request))

# exempt insertlog from CSRF protection, or programs will not be able to submit their statistics!
@csrf_exempt
def insertlog(request):

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

    #raise Http404 # decoy 404 to throw-off people who might otherwise find the URL and spam fake statistics at us
    return HttpResponse('Thank you for participating!')

# returns the censored results of a reverse-DNS lookup
# eg mycomputername.llnl.gov becomes llnl.gov
def _censored_reverse_dns(ip):
    try:
        host = socket.gethostbyaddr(ip)[0]
        m = re.match(r'.+\.(\w+?\.\w+?)$', host)
        return m.group(1)
    except socket.herror:
        return 'Unknown'

# censors an IP address by zeroing-out the last octet
# (assumes IPv4)
def _censor_ip(ip):
    # from beginning of string, matches the first three sets of 1-3 digits separated by a period
    m = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3})', ip) 
    return m.group(1) + ".0"

