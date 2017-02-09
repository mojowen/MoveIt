#!/usr/bin/python

from ConfigParser import RawConfigParser
import httplib
import os
import sys
import socket
sys.path.append('/home/mojowen/MoveIt')

from models.webfaction import WebFaction
from models.mail import send_mail

config = RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config/secrets.ini'))

wf = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )

websites = wf.server.list_websites(wf.session_id)
exceptions = ['Hubot']
output = []

def get_head(domain):
    conn = httplib.HTTPConnection(domain, port=80)
    conn.request('HEAD','/')
    return conn.getresponse()

def check_site(website, follow=True):
    res = get_head(website)
    if res.status / 100 == 3:
        location = [hd for hd in res.getheaders() if hd[0] == 'location'][0][1]
        location = [st for st in location.replace('http', '').split('/') if len(st) > 1][0]
        return check_site(location, False) # Follow one redirect
    else:
        return res

for website in websites:
    if website['name'] not in exceptions:
        main_domain = website['subdomains'][0]
        main_domain = (website['subdomains'][1] if
                       '.scottduncombe.com' in main_domain
                       and len(website['subdomains']) > 1
                       else main_domain)
        try:
            res = check_site(main_domain)
            if res.status != 200:
                output.append("%s at %s responded with a %d" %
                              (website['name'], main_domain, res.status))
        except socket.gaierror:
            output.append("%s at %s returned name or service not known - is the domain ok?" %
                          (website['name'], main_domain))

if len(output) > 0:
    send_mail("\n".join(output), "Uptime Report")

