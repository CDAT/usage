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
import math
from world_regions.models import Region
import copy
from ast import literal_eval
from itertools import tee, islice, chain, izip
from six import string_types
import time
from urllib import urlopen
# from django.conf.settings import PROJECT_ROOT
import collections


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


def platform_bar(request):
    if request.user.is_authenticated():
        source = Source.objects.all()
        net_info = NetInfo.objects.all()
        action = Action.objects.all()
        log_event = LogEvent.objects.all()
        error = Error.objects.all()
        machine = Machine.objects.all()
        # user = User.objects.all()

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
        # user_meta = User._meta
        netinfo_meta = NetInfo._meta
        source_meta = Source._meta
        action_meta = Action._meta
        logevent_meta = LogEvent._meta

        current_path = request.get_full_path()


        return render_to_response('session_stats/platform_bar.html', {'current_path': current_path, 'source': source, 'net_info': net_info, 'action': action, 'log_event': log_event, 'error': error, 'machine': machine, 'mach_meta': mach_meta, 'netinfo_meta': netinfo_meta, 'source_meta': source_meta, 'action_meta': action_meta, 'logevent_meta': logevent_meta, 'd_count': d_count, 'l_count': l_count, 'm_count': m_count, 'l_graph': l_graph, 'm_graph': m_graph, 'd_graph': d_graph, 'sl_graph': sl_graph, 'sm_graph': sm_graph, 'sd_graph': sd_graph }, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def all_years_pie(request):
    if request.user.is_authenticated():
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
            if sesh.startDate.month == 1:
                january += 1
            if sesh.startDate.month == 2:
                february += 1
            if sesh.startDate.month == 3:
                march += 1
            if sesh.startDate.month == 4:
                april += 1
            if sesh.startDate.month == 5:
                may += 1
            if sesh.startDate.month == 6:
                june += 1
            if sesh.startDate.month == 7:
                july += 1
            if sesh.startDate.month == 8:
                august += 1
            if sesh.startDate.month == 9:
                september += 1
            if sesh.startDate.month == 10:
                october += 1
            if sesh.startDate.month == 11:
                november += 1
            if sesh.startDate.month == 12:
                december += 1


            months =[0,1,2,3,4,5,6,7,8,9,10,11]
            monthdata = [january,february,march,april,may,june,july,august,september,october,november,december]
            lineData = [[0,january],[1,february],[2, march],[3,april],[4, may],[5, june],[6, july],[7, august],[8, september],[9, october],[10, november],[11, december]]

        return render_to_response('time_stats/all_years_pie.html', { 'session': session, 'stuff': stuff, 'january': january, 'february': february, 'march': march, 'april': april, 'may': may, 'june': june, 'july': july, 'august': august, 'september': september, 'october': october, 'november': november, 'december': december, 'lineData': lineData, 'months': months, 'monthdata': monthdata }, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def world_stats(request):
    if request.user.is_authenticated():
        netinfo = NetInfo.objects.all()
        countries = []
        cities = []
        testing = []
        dup_testing = []
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
                dup_region = []
                d_region = "duplicate"
                dup_region.append(d_region)
                dup_region.append(inc)
                dup_testing.append(dup_region)
                rement += 25


        netinfo_meta = NetInfo._meta
        countries.pop(0)
        testing.pop(0)
        dup_testing.pop(0)
        the_size = len(countries)

        for test in dup_testing:
            region = Region.objects.get(countries__country=test[1][0])
            test[0] = region.name

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
        dup_total = []
        dup_size = 25
        la_size = 25
        sub_num = sub_city
        circle_num = 0
        for country in countries:
            rgb_num = random.randint(112, 220)
            sec_rgb_num = random.randint(79, 220)
            third_rgb_num = random.randint(79, 220)
            # print rgb_num
            la_count = 0
            okay = []
            dup_okay = []
            for net in netinfo:
                if net.country == country:
                   la_count += 1 
            okay.append(country)
            okay.append(la_count)
            okay.append(la_size)

            dup_okay.append(country)
            dup_okay.append(la_count)
            dup_okay.append(la_size)
            stuff = "Hello"
            okay.append(stuff)
            okay.append(sub_num)
            okay.append(rgb_num)
            okay.append(sec_rgb_num)
            okay.append(third_rgb_num)
            okay.append(circle_num)

            dup_okay.append(stuff)
            dup_okay.append(sub_num)
            dup_okay.append(rgb_num)
            dup_okay.append(sec_rgb_num)
            dup_okay.append(third_rgb_num)
            dup_okay.append(circle_num)
            sub_num += sub_city
            la_size += 25
            la_future_region = "shred"
            region = Region.objects.get(countries__country=country)
            ala_region = region.name
            la_region = ala_region.encode('ascii', 'ignore')
            dup_all = []
            dup_region = []
            dup_region.append(la_region)
            dup_region.append(dup_size)
            dup_all.append(dup_region)
            # dup_all.append(la_region)
            dup_all.append(dup_okay)
            dup_total.append(dup_all)
            # dup_total.append(la_region)
            # dup_total.append(dup_okay)
            dup_size += 25
            total.append(okay)
            
        all_hits = 0
        for tot in total:
            all_hits += tot[1]

        # dup_all_hits = 0
        # for dup_tot in dup_total:
        #     print dup_tot
        #     # dup_all_hits += dup_tot[1]


        for tot in total:
            num_circ = float(tot[1])/all_hits
            num_circ = num_circ * 100
            num_circ = math.ceil(num_circ)
            num_circ += 3.5
            tot[8] = num_circ

        for dup_tot in dup_total:
            num_circ = float(dup_tot[1][1])/all_hits
            num_circ = num_circ * 100
            num_circ = math.ceil(num_circ)
            num_circ += 3.5
            dup_tot[1][8] = num_circ

        for city in new_cities:
            cool_count = 0
            for net in netinfo:
                if city[1] == net.city:
                    cool_count += 1
            city.append(cool_count)

        for tot in total:
            c_name = pycountry.countries.get(alpha_2=tot[0])
            tot[0] = c_name.name

        for dup_tot in dup_total:
            c_name = pycountry.countries.get(alpha_2=dup_tot[1][0])
            dup_tot[1][0] = c_name.name

        for dup_tot in dup_total:
            ciu = []
            for city in new_cities:
                ciudad =[]
                if city[0] == dup_tot[1][0]:
                    ciudad.append(city[1])
                    ciudad.append(city[2])
                    ciudad.append(city[3])
                    ciu.append(ciudad)
            dup_tot[1][3] = ciu
            
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
        dup_total = sorted(dup_total, key=operator.itemgetter(1), reverse=True)
        # dup_total = sorted(dup_total, key=lambda x : x[1][0])

        dupregion_size = 67
        for duptot in dup_total:
            duptot[0][1] = dupregion_size
            dupregion_size += 67

        dupthis_size = 67
        for duptot in dup_total:
            duptot[1][2] = dupthis_size
            dupthis_size += 67

        this_size = 67
        for tot in total:
            tot[2] = this_size
            this_size += 67

        dupla_mini_sub_city = 10
        for tot in dup_total:
             tot[1][3] = sorted(tot[1][3], key=operator.itemgetter(2), reverse=True)
             for each in tot[1][3]:
                 each[1] = dupla_mini_sub_city
                 dupla_mini_sub_city += 14

        la_mini_sub_city = 10
        for tot in total:
            # print tot[3][0]
            # tot[3] = sorted(tot[3], key=operator.itemgetter(2), reverse=True)
            # tot[3] = sorted(tot[3], key=operator.itemgetter(2), reverse=True)
            for each in tot[3]:
                each[1] = la_mini_sub_city
                la_mini_sub_city += 14

        all_regions = []
        for duptot in dup_total:
            all_regions.append(duptot[0][0])

        six_jobs = []
        usually = []
        for duptot in dup_total:
            if duptot[0][0] not in six_jobs:
                six_jobs.append(duptot[0][0])
                usually.append(duptot)
            if duptot[0][0] in six_jobs:
                for ush in usually:
                    if ush[0][0] == duptot[0][0]:
                        if ush[1][0] != duptot[1][0]:
                            ush.append(duptot[1])


        tijuana = copy.deepcopy(usually)
        rollie = copy.deepcopy(dup_total)
        better = []
        tots = 0
        for roll in rollie:
           dup_rgb_num = random.randint(112, 220)
           dup_sec_rgb_num = random.randint(79, 220)
           dup_third_rgb_num = random.randint(79, 220)
           que_bueno = len(roll)
           bro = []
           ice = []
           i = 1
           while i < que_bueno:
               ice.append(roll[i])
               i = i+1 
           bro.append(roll[0][0])
           bro.append(roll[0][1])
           bro.append(ice)
           bro.append(dup_rgb_num)
           bro.append(dup_sec_rgb_num)
           bro.append(dup_third_rgb_num)
           bro.append(tots)
           better.append(bro)


        change_this = 107
        dont_lose = copy.deepcopy(better)
        checked = []
        gaame = []
        for dont in dont_lose:
            if dont[0] not in gaame:
                thiiis = copy.deepcopy(dont)
                thiiis.pop(0)
                thiiis.pop(0)
                que = thiiis[0]
                que_length = len(que)
                total = 0
                for each in que:
                    total += each[1]
                dont[6] = total
                gaame.append(dont[0])
                checked.append(dont)

        for cp in tijuana:
            cp.pop(0)

        checked = sorted(checked, key=operator.itemgetter(6), reverse=True)

        for each in checked:
            each[1] = change_this
            change_this += 106

        switch = 67
        for each in checked:
            for each_country in each[2]:
                each_country[2] = switch
                switch += 67

        chase = 10
        for perk in checked:
            for switch in perk[2]:
               for proof in switch[3]:
                    proof[1] = chase
                    chase += 14

        return render_to_response('global_stats/world_stats.html', {'checked': checked, 'better': better, 'tijuana': tijuana, 'usually': usually, 'dup_total': dup_total, 'ciu': ciu, 'total': total, 'testing': testing, 'countries': countries, 'netinfo': netinfo, 'netinfo_meta': netinfo_meta }, context_instance = RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def geo_stats(request):
    if request.user.is_authenticated():
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
            # print c_name.name
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
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


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

    cool_strings = json.dumps(sup_strings)

    return render_to_response('session_stats/calendar_data.html', { 'cool_strings': cool_strings, 'la_strings': la_strings, 'stuff_care': stuff_care, 'duration': duration, 'total_sesh': total_sesh, 'start_sesh': start_sesh, 'end_sesh': end_sesh, 'session': session, 'data': "Hello" }, context_instance = RequestContext(request))


def bar_sesh(request):
    if request.user.is_authenticated():
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
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def show_log(request):
    '''
    Renders the logs.
    '''
    current_path = request.get_full_path()
    machine = Machine.objects
    return render_to_response('showlog.html', {'current_path': current_path, 'machine': machine
    }, context_instance=RequestContext(request))


def survey(request):
    '''
    Renders the help page.
    '''
    return render_to_response('survey.html', {}, context_instance=RequestContext(request))

def help(request):
    '''
    Renders the help page.
    '''
    return render_to_response('help.html', {}, context_instance=RequestContext(request))


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
    if request.user.is_authenticated():
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
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def testing(request):
    if request.user.is_authenticated():
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

        actions = Action.objects.all()
        action_meta = Action._meta

        act_names = []
        for act in actions:
           if ' ' in act.name:
               stuff = act.name
               new_stuff = stuff.split()
               act_names.append(new_stuff[0])
           if ' ' not in act.name:
               act_names.append(act.name)


        cool = numpy.unique(act_names)
        all_names = []
        for name in cool:
            func_names = []

            func_names.append(name)
            count = 0
            for act in act_names:
                if name == act:
                   count += 1 
            func_names.append(count)
            all_names.append(func_names)

        all_names = json.dumps(all_names)

        return render_to_response('testing/testing.html', { 'all_names': all_names, 'req': request, 'lon': lon, 'lat': lat }, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))

def nested_chart(request):
    if request.user.is_authenticated():
        actions = Action.objects.all()
        action_meta = Action._meta

        act_names = []
        for act in actions:
           if 'Error' not in act.name:
               if ' ' in act.name:
                   stuff = act.name
                   new_stuff = stuff.split()
                   act_names.append(new_stuff[0])
               if ' ' not in act.name:
                   act_names.append(act.name)

        cool = numpy.unique(act_names)
        all_names = []
        for name in cool:
            func_names = []
            sub_list = []

            func_names.append(name)
            count = 0 
            for act in act_names:
                if name == act:
                   count += 1 
            func_names.append(count)
            func_names.append(sub_list)
            all_names.append(func_names)

        admire = []
        for name in cool:
            if "." not in name:
               admire.append(name) 

        yeah = []
        chillin = copy.deepcopy(all_names)
        for ad in admire:
            infinity = []
            colder = []
            count = 0
            for halo in chillin:
                if ad == halo[0]:
                    count += halo[1]
                if ad in halo[0]:
                    if ad != halo[0]:
                        mask = []
                        tumblr = halo[0].split(".")
                        mask.append(tumblr[1])
                        mask.append(halo[1])
                        colder.append(mask)
            infinity.append(ad)
            infinity.append(count)
            infinity.append(colder)
            yeah.append(infinity)

        plan = []
        for fine in yeah:
            free = []
            yup = []
            if len(fine[2]) != 0:
                count = 0
                for previous, item, nxt in previous_and_next(fine[2]):
                    if item[0] in yup:
                        yup.append(item[1]) 
                    if item[0] not in yup:
                        yup.append(item[0])
                        yup.append(item[1])
                free.append(fine[0])
                free.append(yup)
                plan.append(free)

        growth = []
        for elegance in plan:
            learn = []
            count = 0
            for previous, item, nxt in previous_and_next(elegance[1]):
                if isinstance(item, (int, long)):
                    count += item
                    if nxt is None:
                        learn.append(count)
                if isinstance(item, string_types):
                    if count != 0:
                        learn.append(count)
                        count = 0
                    learn.append(item)
            growth.append(learn)
            
        huh = []
        for fine in yeah:
            if len(fine[2]) != 0:
                for grow in growth:
                    if fine[2][0][0] == grow[0]:    
                        fine[2] = grow
                    


        dup_all = copy.deepcopy(all_names)
        faith = []
        hope = []
        sub_states = []
        fake = 0
        for fade in dup_all:
            if '.' in fade[0]:
                states = fade[0].split('.')
                fade[0] = states[0]
                que_bueno = []
                nested_bueno = []
                try:
                    que_bueno.append(states[1])
                    try:
                        nested_bueno.append(states[2])
                        try: 
                            super_nested = []
                            super_nested.append(states[3])
                            nested_bueno.append(super_nested)
                            # nested_bueno.append(states[3])
                        except IndexError:
                            pass
                            #print 'sorry, no 3'
                    except IndexError:
                        pass
                        #print 'sorry, no 2'
                except IndexError:
                    pass
                    #print 'sorry, no 1'
                que_bueno.append(nested_bueno)
                fade[2].append(que_bueno)

        top_hier = []
        for dup in dup_all:
            if dup[0] not in top_hier:
                nested_hier = []
                nested_hier.append(dup[0])
                nested_hier.append([])
                top_hier.append(nested_hier)
            for d in dup[2]:
                for e in d:
                    pass

        sick = []
        idgt = []
        bay = []
        for dup in dup_all:
            laugh = []
            if dup[0] not in sick:
                sick.append(dup[0])
                bay.append(dup[0])
            try:
                if dup[2]: 
                    if dup[2][0][0] not in idgt:
                        idgt.append(dup[2][0][0])
                        laugh.append(dup[0])
                        laugh.append(dup[2][0][0])
                        sick.append(laugh)
            except IndexError:
                print "NAH BRO"


        bed = []
        for not_sick in sick:
            if type(not_sick) == list:
                if not_sick[0] not in bed:
                    pass
                if not_sick[0] in bed:
                    for b in bed:
                        if b == not_sick[0]:
                            this = []
            if type(not_sick) != list:
                pass

        bay = json.dumps(bay)
        sick = json.dumps(sick)
        idgt = json.dumps(idgt)
        all_names = json.dumps(all_names)
        admire = json.dumps(admire)
        yeah = json.dumps(yeah)
        return render_to_response('action_stats/nested_chart.html', { 'growth': growth, 'plan': plan, 'yeah': yeah, 'admire': admire, 'bay': bay, 'bed': bed, 'idgt': idgt, 'sick': sick, 'dup_all': dup_all, 'sub_states': sub_states, 'faith': faith, 'hope': hope, 'cool': cool, 'all_names': all_names, 'act_names': act_names, 'action_meta': action_meta, 'actions': actions }, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)


def most_used_pie(request):
    actions = Action.objects.all()
    action_meta = Action._meta

    act_names = []
    for act in actions:
       if 'Error' not in act.name:
           if ' ' in act.name:
               stuff = act.name
               new_stuff = stuff.split()
               act_names.append(new_stuff[0])
           if ' ' not in act.name:
               act_names.append(act.name)

    cool = numpy.unique(act_names)
    all_names = []
    for name in cool:
        func_names = []

        func_names.append(name)
        count = 0
        for act in act_names:
            if name == act:
               count += 1 
        func_names.append(count)
        all_names.append(func_names)

    all_names = json.dumps(all_names)
    return render_to_response('action_stats/most_used_pie.html', { 'cool': cool, 'all_names': all_names, 'act_names': act_names, 'action_meta': action_meta, 'actions': actions }, context_instance=RequestContext(request))
    
   
def k_bro(request):
    session = Session.objects.all()
    start_s = []
    end_s = []
    for sesh in session:
        start_s.append(sesh.startDate)
        end_s.append(sesh.lastDate)
    return render_to_response('testing/k_bro.html', { 'start_s': start_s, 'end_s': end_s, 'data': "que bro" }, context_instance=RequestContext(request))


def table(request):
    if request.user.is_authenticated():
        netinfo = NetInfo.objects.all()
        countries = []
        cities = []
        testing = []
        dup_testing = []
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
                dup_region = []
                d_region = "duplicate"
                dup_region.append(d_region)
                dup_region.append(inc)
                dup_testing.append(dup_region)
                rement += 25


        netinfo_meta = NetInfo._meta
        countries.pop(0)
        testing.pop(0)
        dup_testing.pop(0)
        the_size = len(countries)

        for test in dup_testing:
            region = Region.objects.get(countries__country=test[1][0])
            test[0] = region.name

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
        dup_total = []
        dup_size = 25
        la_size = 25
        sub_num = sub_city
        circle_num = 0
        for country in countries:
            rgb_num = random.randint(112, 220)
            sec_rgb_num = random.randint(79, 220)
            third_rgb_num = random.randint(79, 220)
            # print rgb_num
            la_count = 0
            okay = []
            dup_okay = []
            for net in netinfo:
                if net.country == country:
                   la_count += 1 
            okay.append(country)
            okay.append(la_count)
            okay.append(la_size)

            dup_okay.append(country)
            dup_okay.append(la_count)
            dup_okay.append(la_size)
            stuff = "Hello"
            okay.append(stuff)
            okay.append(sub_num)
            okay.append(rgb_num)
            okay.append(sec_rgb_num)
            okay.append(third_rgb_num)
            okay.append(circle_num)

            dup_okay.append(stuff)
            dup_okay.append(sub_num)
            dup_okay.append(rgb_num)
            dup_okay.append(sec_rgb_num)
            dup_okay.append(third_rgb_num)
            dup_okay.append(circle_num)
            sub_num += sub_city
            la_size += 25
            la_future_region = "shred"
            region = Region.objects.get(countries__country=country)
            ala_region = region.name
            la_region = ala_region.encode('ascii', 'ignore')
            dup_all = []
            dup_region = []
            dup_region.append(la_region)
            dup_region.append(dup_size)
            dup_all.append(dup_region)
            # dup_all.append(la_region)
            dup_all.append(dup_okay)
            dup_total.append(dup_all)
            # dup_total.append(la_region)
            # dup_total.append(dup_okay)
            dup_size += 25
            total.append(okay)
            
        all_hits = 0
        for tot in total:
            all_hits += tot[1]

        for tot in total:
            num_circ = float(tot[1])/all_hits
            num_circ = num_circ * 100
            num_circ = math.ceil(num_circ)
            num_circ += 3.5
            tot[8] = num_circ

        for dup_tot in dup_total:
            num_circ = float(dup_tot[1][1])/all_hits
            num_circ = num_circ * 100
            num_circ = math.ceil(num_circ)
            num_circ += 3.5
            dup_tot[1][8] = num_circ

        for city in new_cities:
            cool_count = 0
            for net in netinfo:
                if city[1] == net.city:
                    cool_count += 1
            city.append(cool_count)

        for tot in total:
            c_name = pycountry.countries.get(alpha_2=tot[0])
            tot[0] = c_name.name

        for dup_tot in dup_total:
            c_name = pycountry.countries.get(alpha_2=dup_tot[1][0])
            dup_tot[1][0] = c_name.name

        for dup_tot in dup_total:
            ciu = []
            for city in new_cities:
                ciudad =[]
                if city[0] == dup_tot[1][0]:
                    ciudad.append(city[1])
                    ciudad.append(city[2])
                    ciudad.append(city[3])
                    ciu.append(ciudad)
            dup_tot[1][3] = ciu
            
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
        dup_total = sorted(dup_total, key=operator.itemgetter(1), reverse=True)

        dupregion_size = 67
        for duptot in dup_total:
            duptot[0][1] = dupregion_size
            dupregion_size += 67

        dupthis_size = 67
        for duptot in dup_total:
            duptot[1][2] = dupthis_size
            dupthis_size += 67

        this_size = 67
        for tot in total:
            tot[2] = this_size
            this_size += 67

        dupla_mini_sub_city = 10
        for tot in dup_total:
             tot[1][3] = sorted(tot[1][3], key=operator.itemgetter(2), reverse=True)
             for each in tot[1][3]:
                 each[1] = dupla_mini_sub_city
                 dupla_mini_sub_city += 14

        la_mini_sub_city = 10
        for tot in total:
            for each in tot[3]:
                each[1] = la_mini_sub_city
                la_mini_sub_city += 14

        all_regions = []
        for duptot in dup_total:
            all_regions.append(duptot[0][0])

        six_jobs = []
        usually = []
        for duptot in dup_total:
            if duptot[0][0] not in six_jobs:
                six_jobs.append(duptot[0][0])
                usually.append(duptot)
            if duptot[0][0] in six_jobs:
                for ush in usually:
                    if ush[0][0] == duptot[0][0]:
                        if ush[1][0] != duptot[1][0]:
                            ush.append(duptot[1])


        tijuana = copy.deepcopy(usually)
        rollie = copy.deepcopy(dup_total)
        better = []
        tots = 0
        for roll in rollie:
           dup_rgb_num = random.randint(112, 220)
           dup_sec_rgb_num = random.randint(79, 220)
           dup_third_rgb_num = random.randint(79, 220)
           que_bueno = len(roll)
           bro = []
           ice = []
           i = 1
           while i < que_bueno:
               ice.append(roll[i])
               i = i+1 
           bro.append(roll[0][0])
           bro.append(roll[0][1])
           bro.append(ice)
           bro.append(dup_rgb_num)
           bro.append(dup_sec_rgb_num)
           bro.append(dup_third_rgb_num)
           bro.append(tots)
           better.append(bro)


        change_this = 107
        dont_lose = copy.deepcopy(better)
        checked = []
        gaame = []
        for dont in dont_lose:
            if dont[0] not in gaame:
                thiiis = copy.deepcopy(dont)
                thiiis.pop(0)
                thiiis.pop(0)
                que = thiiis[0]
                que_length = len(que)
                total = 0
                for each in que:
                    total += each[1]
                dont[6] = total
                gaame.append(dont[0])
                checked.append(dont)

        for cp in tijuana:
            cp.pop(0)

        checked = sorted(checked, key=operator.itemgetter(6), reverse=True)

        for each in checked:
            each[1] = change_this
            change_this += 106

        switch = 67
        for each in checked:
            for each_country in each[2]:
                each_country[2] = switch
                switch += 67

        chase = 10
        for perk in checked:
            for switch in perk[2]:
               for proof in switch[3]:
                    proof[1] = chase
                    chase += 14

        checked = json.dumps(checked)
        return render_to_response('global_stats/table.html', {'checked': checked, 'better': better, 'tijuana': tijuana, 'usually': usually, 'dup_total': dup_total, 'ciu': ciu, 'total': total, 'testing': testing, 'countries': countries, 'netinfo': netinfo, 'netinfo_meta': netinfo_meta }, context_instance = RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))
    

def sessions_started_per_day(request):
    if request.user.is_authenticated():
        session = Session.objects.all()
        dates = []
        all_dates = []
        for sesh in session:
            nested = []
            just_date = sesh.startDate.date()
            str_date = sesh.startDate
            strj_date = str_date.strftime('%Y,%-m,%d')
            if strj_date not in dates:
                count = 0
                dates.append(strj_date)
                nested.append(strj_date)
                nested.append(count)
            if nested:
                all_dates.append(nested)

        for sesh in session:
            just_date = sesh.startDate.date()
            str_date = sesh.startDate
            strj_date = str_date.strftime('%Y,%-m,%d')
            for all_d in all_dates:
                if all_d[0] == strj_date:
                    all_d[1] += 1

        for all_d in all_dates:
            all_d[0] = json.dumps(all_d[0])

        return render_to_response('session_stats/sessions_started_per_day.html', {'all_dates': all_dates, 'dates': dates}, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def unique_user_sesh(request):
    if request.user.is_authenticated():
        session = Session.objects.all()
        dates = []
        all_dates = []
        for sesh in session:
            nested = []
            just_date = sesh.startDate.date()
            str_date = sesh.startDate
            strj_date = str_date.strftime('%Y,%-m,%d')
            if strj_date not in dates:
                count = 0
                user_list = []
                dates.append(strj_date)
                nested.append(strj_date)
                nested.append(count)
                nested.append(user_list)
            if nested:
                all_dates.append(nested)

        for all_d in all_dates:
            for sesh in session:
                just_date = sesh.startDate.date()
                str_date = sesh.startDate
                strj_date = str_date.strftime('%Y,%-m,%d')
                if strj_date == all_d[0]:
                   if sesh.user not in all_d[2]:
                        all_d[2].append(sesh.user)
                        all_d[1] += 1

        for all_d in all_dates:
            all_d[0] = json.dumps(all_d[0])
            all_d[2] = []

        return render_to_response('session_stats/unique_user_sesh.html', {'all_dates': all_dates, 'session': session}, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))



def testing_d3(request):
    if request.user.is_authenticated():
        return render_to_response('testing/testing_d3.html', {}, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def hierarchical(request):
    if request.user.is_authenticated():
        return render_to_response('testing/hierarchical.html', {}, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def pre_made(request):
    if request.user.is_authenticated():
        return render_to_response('testing/pre_made.html', {}, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))


def nested_d3(request):
    if request.user.is_authenticated():
        actions = Action.objects.all()
        act_names = []
        for act in actions:
            if 'Error' not in act.name:
                if ' ' in act.name:
                    name = act.name
                    new_name = name.split()
                    act_names.append(new_name[0])
                if ' ' not in act.name:
                    act_names.append(act.name)

        admire = []
        # s = {}
        o_list = []
        for name in act_names:
            if "." in name:
                wee = name.partition('.')
                admire.append(wee[0])
                # s = collections.OrderedDict()
                s = {}
                inner = wee[2].partition('.')
                if "." in wee[2]:
                    away = wee[2].partition('.')
                    # ant = collections.OrderedDict()
                    ant = {}
                    if '.' in away[2]:
                        art = away[2].partition('.')
                        # side = collections.OrderedDict()
                        side = {}
                        side[art[0]] = art[2]
                        ant[away[0]] = side
                        s[wee[0]] = ant
                        # print art
                    else:
                        ant[away[0]] = away[2]
                        s[wee[0]] = ant
                else:    
                    s[wee[0]] = wee[2]
                o_list.append(s)
            if "." not in name:
                admire.append(name)
                # o_list.append(name)
            
        first_l = []
        for name in act_names:
            # first_d = {}
            first_d = collections.OrderedDict()
            second_l = []
            third_l = []
            if "." in name:
                part_name = name.partition('.')
                first_d["key"] = part_name[0]
                if "." in part_name[2]:
                    # second_d = {}
                    second_d = collections.OrderedDict()
                    nested_name = part_name[2].partition('.')
                    second_d["key"] = nested_name[0]
                    if "." in nested_name[2]:
                        # third_d = {}
                        # fourth_d = {}
                        third_d = collections.OrderedDict()
                        fourth_d = collections.OrderedDict()
                        fourth_l = []
                        snested_name = nested_name[2].partition('.')
                        third_d["key"] = snested_name[0]
                        # third_d["value"] = snested_name[2]
                        fourth_d["key"] = snested_name[2]
                        fourth_d["values"] = 0
                        fourth_l.append(fourth_d)
                        third_d["values"] = fourth_l
                        third_l.append(third_d)
                        second_d["values"] = third_l
                        second_l.append(second_d)
                        first_d["values"] = second_l
                        first_l.append(first_d)
                    else:
                        second_d["values"] = nested_name[2]
                        second_l.append(second_d)
                else:
                    # afirst = {}
                      afirst = collections.OrderedDict()
                      af_list = []
                      afirst["key"] = part_name[2]
                      # first_d["lalavalue"] = part_name[2]
                      afirst["values"] = 0
                      af_list.append(afirst)
                      first_d["values"] = af_list
                      first_l.append(first_d)
            else:
                first_d["key"] = name
                first_d["value"] = 0
                first_l.append(first_d)

        eighth_l = []
        im_empty = 'empty'
        dontchange = 0
        total = 0
        check = []
        first_check = 0
        for l in first_l:
            for k, v in l.iteritems():
                if type(v) is unicode:
                    if v not in check:
                        check.append(v)
                        total = 0
                if type(v) is list:
                    for time in v:
                        for f_k, f_v in time.iteritems():
                            if type(f_v) is list:
                                for i in f_v:
                                    for s_k, s_v in i.iteritems():
                                        if type(s_v) is list:
                                            for o in s_v:
                                                # im_empty = 'empty'
                                                for i_k, i_v in o.iteritems():
                                                    if i_v not in eighth_l:
                                                        if type(i_v) is unicode:
                                                            eighth_l.append(i_v)
                                                    if i_v in eighth_l:
                                                        if type(i_v) is unicode:
                                                            if dontchange == 0:
                                                                im_empty = i_v
                                                                dontchange = 1
                                                    if type(i_v) is int:
                                                        if im_empty in eighth_l:
                                                            total += 1
                                                            # i_v += 1
                                                            i_v = total
                                                            o.update({i_k: i_v})



        for l in first_l:
            for k, v in l.iteritems():
                if type(v) is list:
                    for time in v:
                        pass
                        # print time
                        # for f_k, f_v in time.iteritems():
                        #     if type(f_v) is list:
                        #         for i in f_v:
                        #             for s_k, s_v in i.iteritems():
                        #                 if type(s_v) is list:
                        #                     for o in s_v:
                        #                         for i_k, i_v in o.iteritems():
                        #                             if type(i_v) is unicode:
                        #                                 print i_v

        # all_vals = collections.OrderedDict()
        # all_list = []
        # all_vals.update({"key": "usage"})
        # all_vals.update({"values": first_l})
        # all_list.append(all_vals)

        d = {}
        for ad in admire:
            if ad not in d:
                d[ad] = 1
            else:
                d[ad] += 1

        time = collections.OrderedDict()
        la_vals = []
        for key, value in d.iteritems():
            okay = collections.OrderedDict()
            okay["key"] = key
            okay["value"] = value
            la_vals.append(okay) 

        time.update({"key":"usage"})
        time.update({"values":la_vals})
        breathe = []
        breathe.append(time)
        
        jsonData = json.dumps(d)
        outer = {}
        inner_vals = []
        inner_vals.append(jsonData)
        outer.update({'values':inner_vals})
        outer.update({'key':'usage'})
        outer_list = []
        outer_list.append(outer)
        new_jsonData = json.dumps(outer_list)
        with open('statsPage/static/jsondata.json', 'w') as f:
            json.dump(breathe, f)

        with open('statsPage/static/testing.json', 'w') as f:
            json.dump(first_l, f)

        return render_to_response('testing/nested_d3.html', {'first_l': first_l, 'o_list': o_list}, context_instance=RequestContext(request))
    else:
        return render_to_response('showlog.html', {}, context_instance = RequestContext(request))

