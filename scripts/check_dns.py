#!/usr/bin/python

from ConfigParser import RawConfigParser
import httplib
import os
import sys
import socket
import subprocess
sys.path.append('/home/mojowen/MoveIt')

from models.webfaction import WebFaction
from models.mail import send_mail

config = RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config/secrets.ini'))

wf = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )
domains = wf.server.list_domains(wf.session_id)
not_configured = []

for domain in domains:
    process = subprocess.Popen([" ".join(['dig', domain['domain'], 'ns'])], stdout=subprocess.PIPE, shell=True)
    result = process.stdout.read()
    if 'ns1.webfaction.com' not in result:
        not_configured.append(domain['domain'])

print not_configured
