# In this script I dropped comments from blogs and - if they aren't on my shared theme file - added a plugin. Demonstrates
#  > Using SSH class to do a mysql command
#  > Using SSH to do a WordPress/PHP command and using the results (including adding a plugin and checking the theme)
#  > Using SSH class to scan a directory and determine if they're wordpress
#
# YUP!

from models.ssh import *

from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('../config/secrets.ini')


wf = SSH(
    config.get('webfaction-ssh', 'domain'),
    config.get('webfaction-ssh', 'user'),
    config.get('webfaction-ssh', 'pass'),
)

wf.cd('~/webapps')

directories = wf.c('ls')


def strip_wp_grep(result):
    if type(result) is list:
        result = result[0]

    result = result.split(", '")[1]
    result = result.split("'")[0]
    return result



for site in directories:
    
    wf.cd('~/webapps/'+site)
    
    try:
        username = strip_wp_grep( wf.c('grep DB_USER wp-config.php') )
        password = strip_wp_grep( wf.c('grep DB_PASSWORD wp-config.php') )

        drop_comments_sql = ['mysql','-u',username,'--password='+password,'-D',username,'-e','"TRUNCATE wp_comments;"']
        drop_comments_sql = " ".join(drop_comments_sql)
        wf.c(drop_comments_sql)
        print 'Dropped '+site+"'s comments"
        
        jolokia = wf.c('php -r "include_once(\'wp-load.php\'); echo wp_get_theme(); " ')[0]

        if jolokia != 'Jolokia':
            
            wf.c('ln -s  ~/shared/disable-comments.php wp-content/plugins/disable-comments.php')
            
            wp_includes = 'include_once(\'wp-load.php\'); include_once(\'wp-admin/includes/admin.php\'); '
            
            php = 'php -r "'+wp_includes+' activate_plugin(\'disable-comments.php\');" '
            wf.c(php)
            
            print 'Added disable-comments to '+site
            
        
    except:
        print site+' is not a WordPress site'