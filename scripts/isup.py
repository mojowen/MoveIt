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
exceptions = []
output = []

def get_head(domain, secure=False):
    if secure:
        conn = httplib.HTTPSConnection(domain, port=443)
    else:
        conn = httplib.HTTPConnection(domain, port=80)
    conn.request('GET','/')
    return conn.getresponse()

def check_site(website, follow=0, secure=False):
    res = get_head(website, secure=secure)
    if res.status / 100 == 3 and follow < 4:
        location = [hd for hd in res.getheaders() if hd[0] == 'location'][0][1]
        location = location.replace('https://', '').replace('http://', '').split('/')[0]
        return check_site(location, follow + 1, secure=secure) # Follow three redirects
    else:
        return res

secure_sites = sum([website['subdomains'] for website in websites if website['https']], [])

for website in websites:
    if len(website['subdomains']) < 1:
        continue
    if website['name'] not in exceptions:
        main_domain = website['subdomains'][0]
        main_domain = (website['subdomains'][1] if
                       '.scottduncombe.com' in main_domain
                       and len(website['subdomains']) > 1
                       else main_domain)

        if main_domain in secure_sites and not website['https']:
            continue
        try:
            res = check_site(main_domain, secure=website['https'])
            if res.status != 200:
                output.append("%s at %s responded with a %d" %
                              (website['name'], main_domain, res.status))
                continue
            if '<html' not in res.read():
                output.append("%s at %s responded without an html tag" %
                              (website['name'], main_domain))
        except socket.gaierror:
            output.append("%s at %s returned name or service not known - is the domain ok?" %
                          (website['name'], main_domain))

if len(output) > 0:
    print output
    send_mail("\n".join(output), "Uptime Report")
