from models.sites import *
from models.ssh import *
from models.webfaction import *

from ConfigParser import RawConfigParser

config = RawConfigParser()
config.read('config/secrets.ini')

sites = file('config/sites.txt').read().split("\n") # Importing the sites

# Webfaction SSH connection
webfaction = SSH(
    config.get('webfaction-ssh', 'domain'),
    config.get('webfaction-ssh', 'user'),
    config.get('webfaction-ssh', 'pass'),
)

# Bluehost SSH connection
bluehost = SSH(
    config.get('bluehost-ssh', 'domain'),
    config.get('bluehost-ssh', 'user'),
    config.get('bluehost-ssh', 'pass'),
)

# Webfaction API
webfaction_api = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )


for raw_site in sites:
    site = Site(raw_site)

    site.backup_bluehost(bluehost)
    
    site.setup_webfaction_site(webfaction_api)
    
    site.webfaction_backup(webfaction,bluehost,'mojowen@scottduncombe.com')
    
    site.cleanup(webfaction,bluehost)


webfaction.close()
bluehost.close()

# Cleanup and testing a full run
# BONUS: Create new user on wordpress