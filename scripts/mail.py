#!/usr/bin/python

# An SMTP Mail sender

import os
import sys
sys.path.append("/home/mojowen/MoveIt")

from models.mail import send_mail

if __name__ == '__main__':
	subject = (sys.argv[1] if len(sys.argv) > 1 else 'Automated Message from Webfaction')
	to_addrs = (sys.argv[2] if len(sys.argv) > 2 else None)
	raw_msg = "\n".join(sys.stdin.readlines())

	if len(raw_msg) > 0:
		send_mail(raw_msg, subject, to_addrs)
