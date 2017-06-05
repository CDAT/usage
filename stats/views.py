from datetime import datetime, timedelta
from pygeoip import GeoIP, GeoIPError
import re
import socket
import sys
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import *
from django.contrib.sessions.models import Session

if not settings.configured:
    settings.configure()

geoip_city_dat = settings.GEOLITECITY_ABSOLUTE_PATH
geoip_org_dat = settings.GEOORGANIZATION_ABSOLUTE_PATH

# default amount of time which must pass before the same event from the
# same user is logged again
default_sleep_minutes = 30

gic = None
try:
    gic = GeoIP(geoip_city_dat)
except IOError, err:
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
    # we don't want to spam the log with warning messages, so don't do anything
    # here. it's desgined to work without the GeoIP Organization database
    # anyway...
    pass

# set socket default timeout to 5 seconds.
# this setting is used by the reverse-DNS lookup
if hasattr(socket, 'setdefaulttimeout'):
    socket.setdefaulttimeout(5)


def retrieve_session(data, request):
    try:
        thiss = request.environ
        hashed_hostname = request.GET.get('hashed_hostname', '')
        hashed_username = thiss["USER"]
        sesh_key = data
        details = request.META.get('HTTP_USER_AGENT', '')
        hello = details.partition(' ')
        browser = hello[0].partition('/')
        platform = browser[0]
        platform_version = browser[2]
    except KeyError:
        return None

    machine = get_or_make_machine(platform, platform_version, hashed_hostname)
    user = get_or_make_user(hashed_username)

    uncensored_ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

    if uncensored_ip == '0.0.0.0' or uncensored_ip == '127.0.0.1':
        uncensored_ip = request.META.get('HTTP_X_FORWARDED_FOR', '0.0.0.0')

    censored_ip = _censor_ip(uncensored_ip)

    domain = request.META.get('REMOTE_HOST', 'Unknown')
    if domain == '' or 'Unknown':
        domain = _censored_reverse_dns(uncensored_ip)

    # NETINFO
    try:
        netInfo_obj = NetInfo.objects.get(ip=censored_ip)
    except ObjectDoesNotExist as err:
        netInfo_obj = NetInfo()
        try:
            geoIpInfo = gic.record_by_addr(uncensored_ip)
            netInfo_obj.country = geoIpInfo['country_code']
            netInfo_obj.city = geoIpInfo['city']
            if netInfo_obj.city == '':
                netInfo_obj.city = 'Unknown'
            netInfo_obj.latitude = str(geoIpInfo['latitude'])
            netInfo_obj.longitude = str(geoIpInfo['longitude'])
        except (GeoIPError, KeyError, AttributeError, TypeError) as e:
            netInfo_obj.country = '--'
            netInfo_obj.city = "Unknown"
            netInfo_obj.latitude = 0.0
            netInfo_obj.longitude = 0.0
        if gio is not None:
            try:
                netInfo_obj.organization = gio.org_by_addr(uncensored_ip)
            except GeoIPError as e:
                netInfo_obj.organization = 'Unknown'
        netInfo_obj.ip = censored_ip
        netInfo_obj.domain = domain
        netInfo_obj.save()

    try:
        session = Session.objects.get(pk=sesh_key)
    except Session.DoesNotExist:
        session = Session()
        session.user = user
        session.machine = machine
        session.netInfo = netInfo_obj
        session.startDate = datetime.now()
        session.lastDate = session.startDate
        session.token = generate_session_token()
        session.expire_date = datetime.now() + timedelta(days=1)
        session.save()
    return session


@csrf_exempt
def get_session(request):
    if request.method != "GET":
        return HttpResponseBadRequest("GET Only")

    session = retrieve_session(request.GET, request)
    return JsonResponse({"token": str(session.token)})

def take_survey(request):
    json_keyfile_name = 'account_secret.json'
    scopes = [
        'https://www.googleapis.com/auth/surveys',
        'https://www.googleapis.com/auth/surveys.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
    ]

    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scopes)
        http = httplib2.Http()
        auth_http = credentials.authorize(http)
    except clientsecrets.InvalidClientSecretsError, e:
        print ('Unable to setup authorization with the given credentials.  %s'
               % e)
        return

    surveys_service = build('surveys', 'v2', http=auth_http)

    return render_to_response('take_survey.html', {'surveys_service': surveys_service}, context_instance=RequestContext(request))

# exempt logEvent from CSRF protection, or programs will not be able to
# submit their statistics!
@csrf_exempt
def log_event(request, returnLogObject=False):
    '''
    Creates a LogEvent.
    '''
    if request.method != "POST":
        return HttpResponseBadRequest("POST Only")

    if "token" not in request.POST:
        # Need to allow for old-style analytics to still get logged.
        # We can construct the token manually using that info.
        # We can probably safely drop analytics after X% of users are on newer versions
        session = retrieve_session(request.POST, request)
    else:
        try:
            session = Session.objects.get(token=request.POST["token"])
        except Session.DoesNotExist:
            return HttpResponseBadRequest("No matching session")
    
    session.lastDate = datetime.now()
    session.save()

    source = request.POST["source"]
    source_version = request.POST["source_version"]

    try:
        source_obj = Source.objects.get(name=source, version=source_version)
    except Source.DoesNotExist:
        source_obj = Source()
        source_obj.name = source
        source_obj.version = source_version
        source_obj.save()

    action = request.POST["action"]
    # ACTION
    try:
        action_obj = Action.objects.get(name=action)
    except Action.DoesNotExist:
        action_obj = Action()
        action_obj.name = action
        action_obj.save()

    log = LogEvent()
    log.session = session
    log.source = source_obj
    log.action = action_obj
    log.frequency = 1
    log.save()

    if returnLogObject:
        return log
    else:
        if "token" not in request.POST:
            return JsonResponse({"token": session.token})
        return HttpResponse()


# exempt logError from CSRF protection, or programs will not be able to
# submit their statistics!
@csrf_exempt
def log_error(request):
    '''
    Creates an Error object, which contains information about an error that occurred.
    '''
    try:
        # get info from the POST
        description = request.POST.get(
            'description', 'No description provided.')
        severity = request.POST.get('severity', 'Unknown').upper()
        stackTrace = request.POST.get('stack_trace', '')
        userComments = request.POST.get('comments', '')
        executionLog = request.POST.get('execution_log', '')

        # create a LogEntry with the appropriate action
        request.POST = request.POST.copy()  # to make it mutable
        # force it to create unique log events for errors.
        request.POST['sleep'] = 0
        request.POST[
            'action'] = "Error (%s) - %s" % (severity, description[:30])
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
        }, context_instance=RequestContext(request))
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
    # from beginning of string, matches the first three sets of 1-3 digits
    # separated by a period
    m = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3})', ip)
    return m.group(1) + ".0"

