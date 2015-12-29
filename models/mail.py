#!/usr/bin/python

# An SMTP Mail sender function

from ConfigParser import RawConfigParser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from hashlib import md5
import os
import re
from smtplib import SMTP

def send_mail(message, subject, to_addresses=None):
	to_addresses = to_addresses or ['srduncombe@gmail.com']
	if isinstance(to_addresses, str):
		to_addresses = to_addresses.split(',')

	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['To'] = ",".join(to_addresses)

	smtp_send(to_addresses, msg)

def create_multipart_from_html(html):
	msg = MIMEMultipart('alternative')

	text = " ".join(re.sub("<.*?>", " ", html).split())
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')
	msg.attach(part1)
	msg.attach(part2)

	return msg

def send_tracked_html_mail(html_file, subject, to_addresses, tracking_file, tracking_code="TRACKING_CODE", **kwargs):
	if( isinstance(to_addresses, list) ):
		to_addresses = ",".join(to_addresses)

	key = md5()
	key.update(to_addresses)
	key.update(subject)
	key = key.hexdigest()

	with open(html_file, 'r') as fl:
		html = fl.read()

	html = re.sub(tracking_code, key, html)
	msg = create_multipart_from_html(html)

	send_html_mail(msg, subject, to_addresses, **kwargs)

	log_message = "\t".join([key, to_addresses, subject, str(datetime.now())])

	with open(tracking_file, "a") as myfile:
		myfile.write("\n%s" % log_message)


def send_html_mail(message, subject, to_addresses, **kwargs):
	if isinstance(to_addresses, str):
		to_addresses = to_addresses.split(',')

	if isinstance(message, MIMEMultipart):
		msg = message
	else:
		with open(message, 'r') as fl:
			html = fl.read()
		msg = create_multipart_from_html_file(html)

	msg['Subject'] = subject
	msg['To'] = ",".join(to_addresses)

	smtp_send(to_addresses, msg, **kwargs)

def smtp_send(to_addrs, mime_message,
			  from_address=None, from_name=None, from_header=None,
			  smtp_credentials='webfaction-email'):
	from_address = from_address or 'me@scottduncombe.com'
	from_name = from_name or "Scott's Host"
	mime_message['From'] = from_header or "%s <%s>" % (from_name, from_address)

	config = RawConfigParser()
	config.read(os.path.join(os.path.dirname(__file__), '../config/secrets.ini'))

	s = SMTP()
	s.connect(config.get(smtp_credentials,'server'), 587)
	s.starttls()
	s.login(config.get(smtp_credentials,'username'),
			config.get(smtp_credentials, 'password'))
	s.sendmail(from_address, to_addrs, mime_message.as_string())
	s.quit()

