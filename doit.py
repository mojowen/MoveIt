from models.sites import *
from models.ssh import *
from models.webfaction import *

from ConfigParser import RawConfigParser

config = RawConfigParser()
config.read('config/secrets.ini')

sites = file('config/sites.txt').read().split("\n") # Importing the sites

for raw_site in sites:
    site = Site(raw_site)
    
    # Webfaction SSH connection
    webfaction = SSH(
        config.get('webfaction-ssh', 'domain'),
        config.get('webfaction-ssh', 'user'),
        config.get('webfaction-ssh', 'pass'),
        site.webfaction_directory
    )
    
    # Bluehost SSH connection
    bluehost = SSH(
        config.get('bluehost-ssh', 'domain'),
        config.get('bluehost-ssh', 'user'),
        config.get('bluehost-ssh', 'pass'),
        site.bluehost_directory
    )
    
    # Webfaction API
    webfaction_api = WebFaction( config.get('webfaction', 'user'), config.get('webfaction', 'pass') )




# TODO: site model for setting up sites
# TODO: webfaction wordpress method = create app, create website, create domain (and special subdomain)
# TODO: webfaction google apps method = create all the mx records
# TODO: #1 sites bluehost method: backup using mysql, tar.bz2
# TODO: #2 webfactional step: create site... that's it?
# TODO: #3 final step: bluehost ssh - untar - move db - mysql domain change

# BONUS: Create new user on wordpress