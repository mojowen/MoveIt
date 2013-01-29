# In this script I moved WordPress sites between two hosts - BlueHost and WebFaction - using SSH, mysqldump, and the WebFaction API
# It demonstrates:
#  > Using SSH and SCP to move files between sites

## Note, you'll need to make sure keys are exchanged from the host you are moving to the host you're leaving (in this case WebFaction > Bluehost)
## See for a how-to: http://www.howtogeek.com/66776/how-to-remotely-copy-files-over-ssh-without-entering-your-password/

#  > Using WebFaction API to create sites

#  > Using SSH to do a MySQL backup, import, and a command

# See config/sites.txt for the layout of the site. This wont work 100% out of the box - you'll need to modify some of the routes in models/sites.py

from models.sites import *
from models.ssh import *
from models.webfaction import *

# Configruation variables for the various hosts
from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('config/secrets.ini')

# Uses sites.txt to determin which sites to move
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