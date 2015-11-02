from models.sites import Site
from models.ssh import SSH
from models.webfaction import WebFaction

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
wf.set_default_wordpress_admin( config.get('default-wordpress', 'email'), config.get('default-wordpress', 'password'), username=config.get('default-wordpress', 'username') )
# ssh = SSH( config.get('webfaction-ssh', 'domain'), config.get('webfaction-ssh', 'user'), config.get('webfaction-ssh', 'pass') )


import readline # optional, will allow Up/Down/History in the console
import code
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()
