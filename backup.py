#!/usr/bin/python

# This is a script I've got runing - via CRON - on my webfaction sever (that's why it doesn't import )
# You can run it using the backup.py | mail -E "Subject Line" my-email@hotmail.com command - it'll mail you when there's an error or a backup needed 


import commands
import sys

class Local:

    base_dir = None

    def cd(self,dir):
        self.base_dir = dir

    def c(self,command):
        if self.base_dir is not None:
            command = 'cd '+self.base_dir+';'+command

        return commands.getstatusoutput(command)[1]


def strip_wp_grep(result):
    if type(result) is list:
        result = result[0]
    result = result.split(", '")[1]
    result = result.split("'")[0]
    return result

local = Local()
local.cd('~/webapps')

try:
    type_of_backup = sys.argv[1]
except:
    type_of_backup = 'daily'

directory = '~/backup/'+type_of_backup+'/'

directories = local.c('ls').split("\n")

output = ''

for site in directories:
    
    
    try:
        local.cd('~/webapps/'+site)

        backup = directory+site+'.tar.bz2'

        is_wordpress = local.c('ls wp-config.php') == 'wp-config.php'
    
        if is_wordpress:
            password = strip_wp_grep( local.c('grep DB_PASSWORD wp-config.php') )
            user = strip_wp_grep( local.c('grep DB_USER wp-config.php') )
        
            sql = ['mysqldump -u ',user,' --password='+password,user,' > wp-content/db-backup.sql']
            sql = " ".join(sql)
            local.c(sql)
        
            local.c('tar -jcvf '+backup+' wp-content')
            local.c('rm wp-content/db-backup.sql')
        
            php = 'include_once("wp-load.php"); include_once("wp-admin/includes/admin.php"); $updates = get_core_updates(); if( $updates[0]->response != "latest" ) echo "upgrade needed"; '
        
            upgrade = local.c("php -r '%s' " % php )
        
            if upgrade == 'upgrade needed':
                output += site+" needs WordPress upgrade \n"
        
        else:
            local.c('tar -jcvf '+backup+' .')
    except:
        output += "Something went wrong with "+site+"\n"
    
if len(output) > 0:
    print output

# IF ERROR OR WORDPRESS UPGRDATE 
    # print an output and mail it: http://stackoverflow.com/questions/5455684/cron-sending-output-to-file-then-emailing-file-to-me
    # echo "hello world" | mail -s "Backup Report" srduncombe@gmail.com