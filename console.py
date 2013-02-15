#!/usr/local/bin/python

#  This is a script used to test stuff in the console... that's about it.

from models.sites import *
from models.ssh import *
from models.webfaction import *


from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('config/secrets.ini')

def reloader(module):
	import models
	exec( 'reload(models.%s)' % module)
	exec( 'from models.%s import *' % module)
	
	if module == 'webfactoin':
		wf = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )


wf = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )
wf_ssh = SSH( config.get('webfaction-ssh', 'domain'), config.get('webfaction-ssh', 'user'), config.get('webfaction-ssh', 'pass') )


