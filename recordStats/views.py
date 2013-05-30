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
        log = LogEvent()
        log.user = user_obj
        log.machine = machine_obj
        log.netInfo = netInfo_obj
        log.source = source_obj
        log.action = action_obj
        log.save()
