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
import json
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from stats.models import *
from django.conf import settings
import dateutil.parser
import pycountry
import operator


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
        }, context_instance=RequestContext(request))

    # try logging in
    user = authenticate(username = username, password = password)

    # Invalid login
    if user is None:
        return render_to_response('authentication_page.html', {
            'error_message': "Invalid username or password. Please try again.",
        }, context_instance=RequestContext(request))
    # De-activated user
    elif not user.is_active:
        return render_to_response('authentication_page.html', {
            'error_message': "The account you are trying to use has been disabled.<br/>" + 
            "Please contact a system administrator.",
        }, context_instance=RequestContext(request))
    # Valid login, active user
    else:
        login(request, user)
        return HttpResponseRedirect('../')

def hello_world(request):
    source = Source.objects.all()
    net_info = NetInfo.objects.all()
    action = Action.objects.all()
    log_event = LogEvent.objects.all()
    error = Error.objects.all()
    machine = Machine.objects.all()
    user = User.objects.all()

    d_count = 0
    l_count = 0
    m_count = 0
    for mach in machine:
        if mach.platform == 'Darwin':
            d_count += 1
        elif mach.platform == 'Linux':
            l_count += 1
        elif mach.platform == 'Mozilla':
            m_count += 1


    sl_graph = l_count*2
    sm_graph = m_count*2
    sd_graph = d_count*2
    l_graph = l_count*4
    m_graph = m_count*4
    d_graph = d_count*4
    mach_meta = Machine._meta
    user_meta = User._meta
    netinfo_meta = NetInfo._meta
    source_meta = Source._meta
    action_meta = Action._meta
    logevent_meta = LogEvent._meta

    #return render_to_response('hello_world.html', {'data': 'Hello World'}, context_instance=RequestContext(request))
    #return render_to_response('hello_world.html', {'data': whatsthis}, context_instance=RequestContext(request))
    return render_to_response('hello_world.html', {'source': source, 'net_info': net_info, 'action': action, 'log_event': log_event, 'error': error, 'machine': machine, 'user': user, 'mach_meta': mach_meta, 'user_meta': user_meta, 'netinfo_meta': netinfo_meta, 'source_meta': source_meta, 'action_meta': action_meta, 'logevent_meta': logevent_meta, 'd_count': d_count, 'l_count': l_count, 'm_count': m_count, 'l_graph': l_graph, 'm_graph': m_graph, 'd_graph': d_graph, 'sl_graph': sl_graph, 'sm_graph': sm_graph, 'sd_graph': sd_graph }, context_instance=RequestContext(request))
    # return HttpResponse("Hello, World")


def sup_world(request):
    session = Session.objects.all()

    i = 0
    for sesh in session:
        if i == 0:
            stuff = dateutil.parser.parse(str(sesh.startDate))
            i = 1



    january = 0
    february = 0
    march = 0
    april = 0
    may = 0
    june = 0
    july = 0
    august = 0
    september = 0
    october = 0
    november = 0
    december = 0

    for sesh in session:
        if sesh.startDate.month == 0:
            january += 1
        if sesh.startDate.month == 1:
            february += 1
        if sesh.startDate.month == 2:
            march += 1
        if sesh.startDate.month == 3:
            april += 1
        if sesh.startDate.month == 4:
            may += 1
        if sesh.startDate.month == 5:
            june += 1
        if sesh.startDate.month == 6:
            july += 1
        if sesh.startDate.month == 7:
            august += 1
        if sesh.startDate.month == 8:
            september += 1
        if sesh.startDate.month == 9:
            october += 1
        if sesh.startDate.month == 10:
            november += 1
        if sesh.startDate.month == 11:
            december += 1


        months =[0,1,2,3,4,5,6,7,8,9,10,11]
        monthdata = [january,february,march,april,may,june,july,august,september,october,november,december]
        lineData = [[0,january],[1,february],[2, march],[3,april],[4, may],[5, june],[6, july],[7, august],[8, september],[9, october],[10, november],[11, december]]

    return render_to_response('sup_world.html', { 'session': session, 'stuff': stuff, 'january': january, 'february': february, 'march': march, 'april': april, 'may': may, 'june': june, 'july': july, 'august': august, 'september': september, 'october': october, 'november': november, 'december': december, 'lineData': lineData, 'months': months, 'monthdata': monthdata }, context_instance=RequestContext(request))

def world_stats(request):
    session = Session.objects.all()
    netinfo = NetInfo.objects.all()
    countries = []
    cities = []
    testing = []
    rement = 0
    print "inside world_stats"
    print "inside world_stats"
    print "inside world_stats"
    for net in netinfo:
        breathe = []
        breathe.append(net.country)
        breathe.append(net.city)
        cities.append(breathe)
        if net.country not in countries: 
            inc = []
            countries.append(net.country)
            # inc.append(net.country)
            inc.append(net.country)
            inc.append(rement)
            testing.append(inc)
            rement += 25


    netinfo_meta = NetInfo._meta
    countries.pop(0)
    testing.pop(0)
    the_size = len(countries)
    increm = []
    i = 0
    ent = 25 
    while i < the_size:
       increm.append(ent)
       ent += 25
       i+=1


    cities.pop(0)
    new_cities = []
    no_reps = []

    the_length = len(countries);
    print the_length
    sub_city = float(1000)/the_length
    mini_sub_city = 10
    print sub_city

    for cit in cities:
        if cit[1] != "Unknown":
            if cit[1] not in no_reps:
                no_reps.append(cit[1])
                c_name = pycountry.countries.get(alpha_2=cit[0])
                cit[0] = c_name.name
                new_c = []
                new_c.append(cit[0])
                new_c.append(cit[1])
                new_c.append(mini_sub_city)
                mini_sub_city += 14
                new_cities.append(new_c)


    # print cities
    # print new_cities
    for test in testing:
        c_name = pycountry.countries.get(alpha_2=test[0])
        test[0] = c_name.name


    total = []
    la_size = 25
    sub_num = sub_city
    for country in countries:
        la_count = 0
        okay = []
        for net in netinfo:
            if net.country == country:
               la_count += 1 
        okay.append(country)
        okay.append(la_count)
        okay.append(la_size)
        stuff = "Hello"
        okay.append(stuff)
        okay.append(sub_num)
        sub_num += sub_city
        la_size += 25
        total.append(okay)
        

    for tot in total:
        c_name = pycountry.countries.get(alpha_2=tot[0])
        tot[0] = c_name.name


    for tot in total:
        ciu = []
        #ciudad =[]
        for city in new_cities:
            ciudad =[]
            if city[0] == tot[0]:
                ciudad.append(city[1])
                ciudad.append(city[2])
                ciu.append(ciudad)
        tot[3] = ciu
        # print len(tot[3])
        

    for tot in total:
        if isinstance(tot, list):
            for to in tot:
                if isinstance(to, list):
                    la_length = len(to)
                    #should = float(sub_city)/la_length
                    #increm = float(sub_city)/la_length
                    #print to
                    #print to
                    #print to
                    #to[1] = increm
                    #increm += increm


    total = sorted(total, key=operator.itemgetter(1), reverse=True)

    this_size = 67
    for tot in total:
        tot[2] = this_size
        this_size += 67

    print total
    return render_to_response('world_stats.html', {'total': total, 'testing': testing, 'data': "Hello World!", 'countries': countries, 'netinfo': netinfo, 'netinfo_meta': netinfo_meta, 'session': session }, context_instance = RequestContext(request))


def show_log(request):
    '''
    Renders the logs.
    '''
    machine = Machine.objects
    return render_to_response('showlog.html', {'machine': machine
    }, context_instance=RequestContext(request))



def show_error_log(request):
    '''
    Renders the logs.
    '''
    return render_to_response('showerrorlog.html', {
    }, context_instance=RequestContext(request))



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
    }, context_instance=RequestContext(request))



def show_debug(request):
    '''
    For debugging use only, will show a form where you can submit log events.
    '''
    if settings.DEBUG:
        return render_to_response('debug.html', {
        }, context_instance=RequestContext(request))
    else:
        raise Http404



def show_debug_error(request):
    '''
    For debugging use only, will show a form where you can submit errors to be logged.
    '''
    if settings.DEBUG:
        return render_to_response('debugerr.html', {
        }, context_instance=RequestContext(request))
    else:
        raise Http404
