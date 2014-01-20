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

	if module == 'webfaction':
		wf = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )


wf = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )
wf.set_default_wordpress_admin( config.get('default-wordpress', 'email'), config.get('default-wordpress', 'password') )
# ssh = SSH( config.get('webfaction-ssh', 'domain'), config.get('webfaction-ssh', 'user'), config.get('webfaction-ssh', 'pass') )


import readline # optional, will allow Up/Down/History in the console
import code
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()