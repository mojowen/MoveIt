# In this script I moved a bunch of recovered backups from my desktop up to new sites in WebFaction
# > demonstrates using the local class
# > demonstrates using SCP locally
#
# that's about it

from models.sites import *
from models.ssh import *
from models.local import *
from models.webfaction import *

# Configruation variables for the various hosts
from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('config/secrets.ini')
import commands

def strip_wp_grep(result):
    result = result.split(", '")[1]
    result = result.split("'")[0]
    return result

# Uses sites.txt to determin which sites to move
sites = file('config/hellersites.txt').read().split("\n") # Importing the sites

webfaction_api = WebFaction( config.get('webfaction-heller', 'user'), config.get('webfaction-heller', 'pass'),config.get('webfaction-heller', 'domain') )

webfaction = SSH(
    config.get('webfaction-heller', 'domain-ssh'),
    config.get('webfaction-heller', 'user'),
    config.get('webfaction-heller', 'pass'),
)

local = Local()

for raw_site in sites:
    site = raw_site.split('\t')
    name = site[0]
    new_domain = site[1]
        
    wf_location = '~/webapps/'+name
    local_location = '~/desktop/heller/*/public_html/'+site[1]


    # Creating WF 
    webfaction_api.create_wordpress( name, new_domain )
  

    # getting rid of webapp content
    webfaction.cd(wf_location)
    webfaction.c('mv wp-content wp-content-old')
    
    
    # moving the site
    local.cd(local_location)      
    local.c('scp -r wp-content bridgetown@web373.webfaction.com:'+wf_location+'/wp-content')
    
    # moving the db backup
    db = strip_wp_grep( local.c('grep DB_USER wp-config.php') )
    local.c('scp ~/desktop/heller/*/mysql/'+db+'.sql bridgetown@web373.webfaction.com:'+wf_location)

    webfaction_mysql_password = strip_wp_grep( webfaction.c('grep "DB_PASSWORD" wp-config.php')[0] )
    webfaction_mysql_username = strip_wp_grep( webfaction.c('grep "DB_USER" wp-config.php')[0] )
    
    # restoring the db
    sql = ['mysql -u',webfaction_mysql_username,'--password='+webfaction_mysql_password,'-D '+webfaction_mysql_username,'< *.sql']
    sql = " ".join(sql)
    webfaction.c(sql)
    
    new_domain = 'http://'+name+'.'+config.get('webfaction-heller', 'domain')
    
    fix_domain = ['mysql -u',webfaction_mysql_username,'--password='+webfaction_mysql_password,'-D '+webfaction_mysql_username,'-e','"UPDATE wp_options SET option_value = \''+new_domain+'\' WHERE option_name IN(\'siteurl\',\'home\');"']
    fix_domain = ' '.join(fix_domain)
    webfaction.c(fix_domain)



