import sys
import re
sys.path.append('app/scripts')
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader, RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
#import  sample_plot_function as spf
from models import *
import hashlib
from django.contrib.auth import authenticate, login


def hello(request):
    return HttpResponse("Hello World")

def show_authentication_page(request):
    return render_to_response('authentication_page.html', {
    }, context_instance=RequestContext(request))

def ajax_getDomainInfo(request):
    if request.user.is_authenticated():
        list=Domains.objects.values('ip','name')

        # convert to JSON
        json_list = str(list)
        json_list = re.sub(r"u'|'", '"', json_list)
        json_list = "{ \"aaData\": " + json_list + "}"

        return HttpResponse(json_list, content_type="application/json")
    else:
        return HttpResponse("Unauthenticated")

def ajax_getLogInfo(request):
    if request.user.is_authenticated():
        # Django doesn't support reverse indexing on QuerySets, so sort backwards and get the first 200 instead.
        results = Access.objects.all().order_by('-date').values('date', 'user', 'source', 'action')
        results = results[:200]
        for r in results:
            # replace datetime objects with a string representation of the date
            r['date'] = r['date'].strftime("%Y-%m-%d %H:%M:%S")
            # resolve foregin keys
            r['user'] = Users.objects.get(pk=r['user']).machine.domain.name
            r['source'] = Sources.objects.get(pk=r['source']).name
            r['action'] = Actions.objects.get(pk=r['action']).name

        # convert to JSON
        json_results = str(results)
        json_results = re.sub(r"u'|'", '"', json_results)
        json_results = "{ \"aaData\":" + json_results + "}"
        return HttpResponse(json_results, content_type="application/json")
    else:
        return HttpResponse("Unauthenticated")


def showlog(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except:
        # Either no username or no password supplied. They tried skipping the login and going
        # straight to the results!
        return HttpResponseRedirect('/log/')

    # try logging in
    user = authenticate(username=username, password=password)

    # Invalid login
    if user is None:
        return render_to_response('authentication_page.html', {
            'error_message': "Invalid username or password. Please try again.",
        }, context_instance=RequestContext(request))
    # De-activated user
    elif not user.is_active:
        return render_to_response('authentication_page.html', {
            'error_message': "The account you are trying ot use has been disabled.<br/>Please contact a system administrator.",
        }, context_instance=RequestContext(request))
    # Valid login, active user
    else:
        login(request, user)
        domain_list=Domains.objects.all()
        allaccess_list=Access.objects.all().order_by('-date')
        access_list=allaccess_list[:200]
        return render_to_response('showlog.html', {
            'domain_list': domain_list,
            'access_list': access_list,
        }, context_instance=RequestContext(request))
   
# exempt insertlog from CSRF protection, or UV-CDAT will not be able to submit statistics!
@csrf_exempt
def insertlog(request):
    # IP address (IPv4 only!)
    try:
        ip=request.POST['REMOTE_ADDR']
    except:
        ip="0.0.0.0"

    # hostname
    try:
        name=request.POST['REMOTE_HOST']
    except Exception, err:
        name='Unknown'

    # platform 
    try:
        platform=request.POST['platform']
    except:
        platform='Unknown'

    # source 
    try:
        source = request.POST['source']
    except:
        source = 'Unknown'

    # action 
    try:
        action = request.POST['action']
    except:
        action = 'Unknown'

    user=hashlib.md5("%s"%(ip)).hexdigest()
    domain=name
    try:
        domain_obj=Domains.objects.get(name=domain,ip=ip)
    except Exception, err:
        domain_obj=Domains()
        domain_obj.name=domain
        domain_obj.ip=ip
        domain_obj.save()
    machine=hashlib.md5(ip).hexdigest()

    try:
        machine_obj=Machines.objects.get(md5=machine)
    except Exception, err:
        machine_obj=Machines()
        machine_obj.md5=machine
        machine_obj.domain=domain_obj
        machine_obj.platform=platform
        machine_obj.save()
    try:
        user_obj=Users.objects.get(md5=user)
    except Exception, err:
        user_obj=Users()
        user_obj.md5=user
        user_obj.machine=machine_obj
        user_obj.save()
    try:
        source_obj=Sources.objects.get(name=source)
    except Exception, err:
        source_obj=Sources()
        source_obj.name=source
        source_obj.save()
    try:
        action_obj=Actions.objects.get(name=action)
    except Exception, err:
        action_obj=Actions()
        action_obj.name=action
        action_obj.save()
    access_obj=Access()
    access_obj.user=user_obj
    access_obj.source=source_obj
    access_obj.action=action_obj
    access_obj.save()
        
    return render_to_response('debug.html', {
        'request': request,
    }, context_instance=RequestContext(request))
