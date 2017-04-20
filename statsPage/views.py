import datetime
import numpy
import hashlib
from pygeoip import GeoIP, GeoIPError
from random import choice, randint
import os
import re
import socket
import sys
import threading
import random
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader, RequestContext
import requests
import json
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from stats.models import *
from django.conf import settings
import dateutil.parser
import pycountry
import operator
# from geopy.geocoders import Nominatim
import reverse_geocoder as rg


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


# def hello_world(request):
def platform_bar(request):
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

    if request.user.is_authenticated:
        print "WE ARE AUTHED"

    return render_to_response('session_stats/platform_bar.html', {'source': source, 'net_info': net_info, 'action': action, 'log_event': log_event, 'error': error, 'machine': machine, 'user': user, 'mach_meta': mach_meta, 'user_meta': user_meta, 'netinfo_meta': netinfo_meta, 'source_meta': source_meta, 'action_meta': action_meta, 'logevent_meta': logevent_meta, 'd_count': d_count, 'l_count': l_count, 'm_count': m_count, 'l_graph': l_graph, 'm_graph': m_graph, 'd_graph': d_graph, 'sl_graph': sl_graph, 'sm_graph': sm_graph, 'sd_graph': sd_graph }, context_instance=RequestContext(request))


def all_years_pie(request):
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

    return render_to_response('time_stats/all_years_pie.html', { 'session': session, 'stuff': stuff, 'january': january, 'february': february, 'march': march, 'april': april, 'may': may, 'june': june, 'july': july, 'august': august, 'september': september, 'october': october, 'november': november, 'december': december, 'lineData': lineData, 'months': months, 'monthdata': monthdata }, context_instance=RequestContext(request))

def world_stats(request):
    netinfo = NetInfo.objects.all()
    countries = []
    cities = []
    testing = []
    rement = 0
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

    cities.pop(0)
    new_cities = []
    no_reps = []

    the_length = len(countries);
    sub_city = float(1000)/the_length
    mini_sub_city = 10

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


    for test in testing:
        c_name = pycountry.countries.get(alpha_2=test[0])
        test[0] = c_name.name


    total = []
    la_size = 25
    sub_num = sub_city
    for country in countries:
        rgb_num = random.randint(112, 220)
        sec_rgb_num = random.randint(79, 220)
        third_rgb_num = random.randint(79, 220)
        # print rgb_num
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
        okay.append(rgb_num)
        okay.append(sec_rgb_num)
        okay.append(third_rgb_num)
        sub_num += sub_city
        la_size += 25
        total.append(okay)
        
    # print total
    # cool_cities = new_cities
    for city in new_cities:
        cool_count = 0
        for net in netinfo:
            if city[1] == net.city:
                cool_count += 1
        city.append(cool_count)
        # print city

    for tot in total:
        c_name = pycountry.countries.get(alpha_2=tot[0])
        tot[0] = c_name.name

    for tot in total:
        ciu = []
        for city in new_cities:
            ciudad =[]
            if city[0] == tot[0]:
                ciudad.append(city[1])
                ciudad.append(city[2])
                ciudad.append(city[3])
                ciu.append(ciudad)
        tot[3] = ciu
        

    total = sorted(total, key=operator.itemgetter(1), reverse=True)

    temp_list = []
    by_list = []
    dicts = {}
    for tot in total:
        all_of_it = []
        by_country = []
        by_country.append(tot[0])
        sway = []
        for each in tot[3]:
            # by_country.append(each[0])
            temp_list.append(each[0])
            sway.append(each[0])
            by_country.append(sway)
        # by_list.append(by_country)
        by_list.append(by_country)
        all_of_it.append(tot[1])
        all_of_it.append(tot[2])
        all_of_it.append(tot[3])
        # dicts[tot[0]] = tot[3]
        dicts[tot[0]] = all_of_it

    this_size = 67
    for tot in total:
        tot[2] = this_size
        this_size += 67

    la_mini_sub_city = 10
    for tot in total:
        tot[3] = sorted(tot[3], key=operator.itemgetter(2), reverse=True)
        # print tot
        for each in tot[3]:
            each[1] = la_mini_sub_city
            la_mini_sub_city += 14

    # print total
    return render_to_response('global_stats/world_stats.html', {'dicts': dicts, 'by_list': by_list, 'temp_list': temp_list, 'ciu': ciu, 'total': total, 'testing': testing, 'countries': countries, 'netinfo': netinfo, 'netinfo_meta': netinfo_meta }, context_instance = RequestContext(request))


def geo_stats(request):
    netinfo = NetInfo.objects.all()
    countries = []
    cities = []
    testing = []
    passthis = []
    rement = 0 
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
            passthis.append(net.country)
            testing.append(inc)
            rement += 25

    passthis.pop(0)
    countries.pop(0)
    total = []
    for country in countries:
        la_count = 0 
        okay = []
        for net in netinfo:
            if net.country == country:
               la_count += 1 
        okay.append(country)
        okay.append(la_count)
        total.append(okay)
            

    forreal = []
    for cnty in countries:
        c_name = pycountry.countries.get(alpha_2=cnty)
        print c_name.name
        cnty = c_name.name
        forreal.append(c_name.name)

    for tot in total:
        c_name = pycountry.countries.get(alpha_2=tot[0])
        c_the_name = str(c_name.name)
        #tot[0] = c_name.name
        tot[0] = str(c_the_name)


    total = sorted(total, key=operator.itemgetter(1), reverse=True)
    # js_data = simplejson.dumps(my_dict)
    forreal = json.dumps(forreal)
    bruh = json.dumps(total)

    array = [['X', 'Y', 'Z'], [1, 2, 3], [4, 5, 6]]
    context = {}
    context['data'] = {'Python': 52.9, 'Jython': 1.6, 'Iron Python': 27.7}
    context['line_data'] = list(enumerate(range(1, 20)))
    return render_to_response('global_stats/geo_stats.html', { 'array': json.dumps(array), 'forreal': forreal, 'countries': countries, 'passthis': passthis, 'bruh' : bruh, 'total': total, 'data': context['data'], 'line_data': context['line_data'] }, context_instance = RequestContext(request))


def calendar_data(request):
    session = Session.objects.all()
    user = User.objects.all()
    start_sesh = []
    end_sesh = []
    total_sesh = []
    duration = []
    stuff_care = []
    la_strings = []
    sup_strings = []
    for sesh in session:
        nested_sesh = []
        start_sesh.append(sesh.startDate)
        end_sesh.append(sesh.lastDate)
        nested_sesh.append(sesh.startDate)
        nested_sesh.append(sesh.lastDate)
        total_sesh.append(nested_sesh)
        duration.append(nested_sesh)
        duration.append(sesh.lastDate - sesh.startDate)
        duration.append(sesh.netInfo)
        stuff_care.append(nested_sesh)
        # print(sesh.lastDate - sesh.startDate)
        start_s = sesh.startDate
        end_s = sesh.lastDate
        # la_strings.append(start_s.strftime('%m/%d/%Y')) 
        # la_strings.append(end_s.strftime('%m/%d/%Y')) 
        the_strings = []
        # the_strings.append("SUP")
        # the_strings.append(start_s.strftime('%Y, %-m, %-d')) 
        # the_strings.append(end_s.strftime('%Y, %-m, %-d')) 
        the_strings.append(start_s.strftime('%b, %-d, %Y, %I:%M %p')) 
        the_strings.append(end_s.strftime('%b, %-d, %Y, %I:%M %p')) 
        sup_strings.append(the_strings);
        la_strings.append("SUP")
        la_strings.append(start_s.strftime('%Y, %-m, %-d')) 
        la_strings.append(end_s.strftime('%Y, %-m, %-d')) 

    mmkay = json.dumps(la_strings)
    cool_strings = json.dumps(sup_strings)

    return render_to_response('session_stats/calendar_data.html', { 'cool_strings': cool_strings, 'mmkay': mmkay, 'la_strings': la_strings, 'stuff_care': stuff_care, 'duration': duration, 'total_sesh': total_sesh, 'start_sesh': start_sesh, 'end_sesh': end_sesh, 'session': session, 'data': "Hello" }, context_instance = RequestContext(request))


def bar_sesh(request):
    session = Session.objects.all()
    user = User.objects.all()
    sup_strings = []
    the_diff = []
    big_cool_diff = []
    cool_diff = []
    for sesh in session:
        # cool_diff = []
        nested_sesh = []
        start_s = sesh.startDate
        end_s = sesh.lastDate
        the_strings = []
        the_strings.append(start_s.strftime('%b, %-d, %Y, %I:%M %p')) 
        the_strings.append(end_s.strftime('%b, %-d, %Y, %I:%M %p')) 
        time_diff = end_s-start_s
        # time_diff = time_diff.strftime('%B, %-d, %Y, %Y:%M %p')
        if time_diff != datetime.timedelta(seconds=0):
            time_vars = []
            the_diff.append(str(time_diff))
            time_vars.append(start_s.strftime('%Y'))
            time_vars.append(start_s.strftime('%B'))
            time_vars.append(start_s.strftime('%-m'))
            time_vars.append(start_s.strftime('%-I %p'))
            #cool_diff.append(start_s.strftime('%b, %-d, %Y, %I:%M %p'))
            # cool_diff.append(str(time_diff))
            time_str = str(time_diff)
            cool_diff.append(time_str)
            cool_diff.append(time_vars)
            big_cool_diff.append(cool_diff)
            sup_strings.append(the_strings)


    one_min_sesh = []
    one_hour_sesh = []
    half_day_sesh = []
    one_day_sesh = []
    one_week_sesh = []
    few_weeks_sesh = []
    one_month_sesh = []
    two_month_sesh = []
    three_plus_sesh = []

    one_min = 0
    one_hour = 0
    half_day = 0
    one_day = 0 
    one_week = 0
    few_weeks = 0
    one_month = 0
    two_month = 0
    three_plus = 0

    for sesh in session:
        start_s = sesh.startDate
        end_s = sesh.lastDate
        time_diff = end_s-start_s
        if time_diff >= datetime.timedelta(weeks=12):
            three_plus_sesh.append(str(time_diff))
            three_plus += 1
        if time_diff < datetime.timedelta(weeks=12) and time_diff >= datetime.timedelta(weeks=8):
            two_month_sesh.append(str(time_diff))
            two_month += 1
        if time_diff < datetime.timedelta(weeks=8) and time_diff >= datetime.timedelta(weeks=4):
            one_month_sesh.append(str(time_diff))
            one_month += 1
        if time_diff <= datetime.timedelta(weeks=4) and time_diff > datetime.timedelta(weeks=1):
            few_weeks_sesh.append(str(time_diff))
            few_weeks += 1
        if time_diff <= datetime.timedelta(weeks=1) and time_diff > datetime.timedelta(days=1):
            one_week_sesh.append(str(time_diff))
            one_week += 1
        if time_diff <= datetime.timedelta(days=1) and time_diff > datetime.timedelta(hours=12):
            one_day_sesh.append(str(time_diff))
            one_day += 1
        if time_diff <= datetime.timedelta(hours=12) and time_diff > datetime.timedelta(hours=1):
            half_day_sesh.append(str(time_diff))
            half_day += 1
        if time_diff <= datetime.timedelta(hours=1) and time_diff > datetime.timedelta(minutes=1):
            one_hour_sesh.append(str(time_diff))
            one_hour += 1
        if time_diff <= datetime.timedelta(minutes=1) and time_diff > datetime.timedelta(seconds=0):
            one_min_sesh.append(str(time_diff))
            one_min += 1


    all_the_seshs = {}
    all_the_seshs['one_min_sesh'] = one_min_sesh
    all_the_seshs['one_hour_sesh'] = one_hour_sesh
    all_the_seshs['half_day_sesh'] = half_day_sesh
    all_the_seshs['one_day_sesh'] = one_day_sesh
    all_the_seshs['one_week_sesh'] = one_week_sesh
    all_the_seshs['few_weeks_sesh'] = few_weeks_sesh
    all_the_seshs['one_month_sesh'] = one_month_sesh
    all_the_seshs['two_month_sesh'] = two_month_sesh
    all_the_seshs['three_plus_sesh'] = three_plus_sesh

    all_seshs = {}
    all_seshs['one_min'] = one_min
    all_seshs['one_hour'] = one_hour
    all_seshs['half_day'] = half_day
    all_seshs['one_day'] = one_day
    all_seshs['one_week'] = one_week
    all_seshs['few_weeks'] = few_weeks
    all_seshs['one_month'] = one_month
    all_seshs['two_month'] = two_month
    all_seshs['three_plus'] = three_plus

    la_diff = []
    for each in the_diff:
        # if ('days' or 'day') not in each:
        if 'day' not in each:
            zero = '0 day, '
            zero += each
            la_diff.append(zero)
        else:
            la_diff.append(each)


    # cool_diff = json.dumps(cool_diff)
    cool_strings = json.dumps(sup_strings)

    return render_to_response('session_stats/bar_sesh.html', { 'all_seshs': all_seshs, 'all_the_seshs': all_the_seshs, 'cool_diff': cool_diff, 'big_cool_diff': big_cool_diff, 'la_diff': la_diff, 'sup_strings': sup_strings, 'the_diff': the_diff, 'cool_strings': cool_strings, 'session': session }, context_instance = RequestContext(request))


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


def pie_by_year(request):
    session = Session.objects.all()
    i = 0
    for sesh in session:
        if i == 0:
            stuff = dateutil.parser.parse(str(sesh.startDate))
            i = 1

    years = []
    for sesh in session:
       years.append(sesh.startDate.year)

    cool = numpy.unique(years)
    all_the_years = []
    total_years = []
    todo = []

    for year in cool:
        all_the_years.append(year)
        total_years.append(year)
        the_coolest = []
        for sesh in session:
            if year == sesh.startDate.year:
                the_months = []
                the_months.append(sesh.startDate.month)
                the_coolest.append(the_months)
        all_the_years.append(the_coolest)
        todo.append(year)
        todo.append(all_the_years)


    deck = {}
    for year in cool:
        la_coolest = []
        for sesh in session:
            if year == sesh.startDate.year:
                la_months = []
                la_months.append(sesh.startDate.month)
                la_coolest.append(la_months)
                deck[year] = la_coolest

    tot_size = len(total_years)
    return render_to_response('time_stats/pie_by_year.html', { 'deck': deck, 'todo': todo, 'total_size': tot_size, 'total_years': total_years, 'all_the_years': all_the_years }, context_instance=RequestContext(request))


def testing(request):
    session = Session.objects.all()
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']

    latlon = []
    latlon.append(lat)
    latlon.append(lon)
    omg = rg.search(latlon)
    la_state = omg[0]['admin1']
    la_country = omg[0]['cc']
    all_the_info = pycountry.countries.get(alpha_2=la_country)
    country_name = all_the_info.name
    print omg[0]['name']
    print la_state
    print la_country
    print all_the_info
    print country_name
    print omg
    # geolocator = Nominatim()
    # location = geolocator.reverse(latlon)
    # print(location.address)

    actions = Action.objects.all()
    action_meta = Action._meta

    act_names = []
    for act in actions:
       if ' ' in act.name:
           # act_names.append(act.name)
           stuff = act.name
           new_stuff = stuff.split()
           act_names.append(new_stuff[0])
       if ' ' not in act.name:
           act_names.append(act.name)


    # first = True
    cool = numpy.unique(act_names)
    # all_names = {} 
    all_names = []
    for name in cool:
        func_names = []
        # if first == True:
        #     func_names.append("Function")
        #     func_names.append("Count")
        #     all_names.append(func_names)
        #     func_names = []
        #     first = False

        func_names.append(name)
        count = 0
        for act in act_names:
            if name == act:
               count += 1 
        func_names.append(count)
        all_names.append(func_names)
        # all_names[name] = func_names

    all_names = json.dumps(all_names)

    return render_to_response('testing/testing.html', { 'all_names': all_names, 'req': request, 'lon': lon, 'lat': lat }, context_instance=RequestContext(request))



# def late_april_stats(request):
def most_used_pie(request):
    actions = Action.objects.all()
    action_meta = Action._meta

    act_names = []
    for act in actions:
       if 'Error' not in act.name:
           if ' ' in act.name:
               # act_names.append(act.name)
               stuff = act.name
               new_stuff = stuff.split()
               act_names.append(new_stuff[0])
           if ' ' not in act.name:
               act_names.append(act.name)


    # first = True
    cool = numpy.unique(act_names)
    # all_names = {} 
    all_names = []
    for name in cool:
        func_names = []
        # if first == True:
        #     func_names.append("Function")
        #     func_names.append("Count")
        #     all_names.append(func_names)
        #     func_names = []
        #     first = False

        func_names.append(name)
        count = 0
        for act in act_names:
            if name == act:
               count += 1 
        func_names.append(count)
        all_names.append(func_names)
        # all_names[name] = func_names

    all_names = json.dumps(all_names)

    return render_to_response('action_stats/most_used_pie.html', { 'cool': cool, 'all_names': all_names, 'act_names': act_names, 'action_meta': action_meta, 'actions': actions }, context_instance=RequestContext(request))
    
    



