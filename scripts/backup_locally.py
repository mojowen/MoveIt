# Similar to doit.py, I'm backing up and sites. But here I'm moving them to a local location.
# It demonstrates:
#  > Using SSH and SCP to move files between sites

## Note, you'll need to make sure keys are exchanged from the host you are moving to the host you're leaving (in this case WebFaction > Bluehost)
## See for a how-to: http://www.howtogeek.com/66776/how-to-remotely-copy-files-over-ssh-without-entering-your-password/

#  > Using SSH to do a MySQL backup, import, and a command

# See config/sites.txt for the layout of the site. This wont work 100% out of the box - you'll need to modify some of the routes in models/sites.py

from models.sites import *
from models.ssh import *
from models.local import *
from models.webfaction import *

# Configruation variables for the various hosts
from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('../config/secrets.ini')

# Uses sites.txt to determin which sites to move
sites = file('../config/sites.txt').read().split("\n") # Importing the sites


# Bluehost SSH connection
bluehost = SSH(
    config.get('bluehost-ssh', 'domain'),
    config.get('bluehost-ssh', 'user'),
    config.get('bluehost-ssh', 'pass'),
)

# Local thing
local = Local()


for raw_site in sites:
    site = Site(raw_site)

    site.backup_bluehost(bluehost)

    site.local_backup(local,config.get('bluehost-ssh', 'user')+'@'+config.get('bluehost-ssh', 'domain'))



bluehost.close()
