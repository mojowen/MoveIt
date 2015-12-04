#!/usr/bin/python

# An SMTP Mail sender function

from ConfigParser import RawConfigParser
from email.mime.text import MIMEText
import os
from smtplib import SMTP

def send_mail(message, subject, to_addresses=None):

	to_addresses = to_addresses or ['srduncombe@gmail.com']
	if isinstance(to_addresses, str):
		to_addresses = to_addresses.split(',')

	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['To'] = ",".join(to_addresses)

	smtp_send(to_addresses, msg)

def smtp_send(to_addrs, mime_message, from_addr=None, from_name=None):
	from_addr = from_addr or 'me@scottduncombe.com'
	from_name = from_name or "Scott's Host"
	mime_message['From'] = "%s <%s>" % (from_name, from_addr)

	config = RawConfigParser()
	config.read(os.path.join(os.path.dirname(__file__), '../config/secrets.ini'))

	s = SMTP()
	s.connect('smtp.webfaction.com')
	s.login(config.get('webfaction-email','username'),
			config.get('webfaction-email', 'password'))
	s.sendmail(from_addr, to_addrs, mime_message.as_string())
	s.quit()

