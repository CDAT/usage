import os
import re

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import Context, loader, RequestContext

def show_login(request):
    """
    Function to show the login page.
    """
    # for POST requests, attempt logging-in
    if request.POST:
        user = authenticate(username = request.POST.get('username', None),
                            password = request.POST.get('password', None))
        redirect_addr = request.POST.get('redir', '')
        if user is not None:
            if user.is_active:
                # login was successful
                login(request, user)
                redirect_addr = _sanitize_redirect(request.POST.get('redir', ''))
                # redirect_addr = 'http://%s/%s' % (request.get_host(), redirect_addr)
                redirect_addr = 'http://%s/%s' % (request.get_host(), redirect_addr + "stats/")
                print redirect_addr
                return HttpResponseRedirect(redirect_addr)
            else:
                return render_to_response('login_form.html', {
                    'redir': redirect_addr,
                    'error_message': 'Account disabled. If you believe this is \
                                      an error, please contact an administrator.',
            }, context_instance = RequestContext(request))
                                                        
        else:
            return render_to_response('login_form.html', {
                    'redir': redirect_addr,
                    'error_message': 'Username or password incorrect.',
            }, context_instance = RequestContext(request))
            
    # for GET requests, render the login page
    else:
        return render_to_response('login_form.html', {
                    'redir': request.GET.get('redir', ''),
                }, context_instance = RequestContext(request))
    
def _sanitize_redirect(targetUrl):
    protocolPrefix = re.compile(r'.*://');
    bannedCharacters = re.compile(r'[<>\s]*')
    sanitizedUrl = re.sub(protocolPrefix, "", targetUrl)
    sanitizedUrl = re.sub(bannedCharacters, "", sanitizedUrl)
    return sanitizedUrl
