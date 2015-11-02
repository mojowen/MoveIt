# In this script I deploy a local site to wordpress
# Things that could be better:
#   > I search the content and overwrite most mentions of the local_url in the content EXCEPT FOR WIDGETS
#   > It's pretty slow! This is shitty. Maybe I need to use git and some sort of diffing. Hmm
#   >


import sys
from models.local import *
from models.ssh import *
from models.moveit_utils import *

# Configruation variables for the various hosts
from ConfigParser import RawConfigParser
config = RawConfigParser()
config.read('config/secrets.ini')

local = Local()

remote = SSH(
    config.get('webfaction-ssh', 'domain'),
    config.get('webfaction-ssh', 'user'),
    config.get('webfaction-ssh', 'pass'),
)

local_directory = sys.argv[1]
remote_directory = sys.argv[2]

local.cd( local_directory )
remote.cd( remote_directory )

# Fetch the remote URL so we can fix things once the db is moved
remote_url = 'http://report.busfedcivic.org' #wordpress_command(remote, 'echo get_option("siteurl");' )[0]
local_url = wordpress_command(local, 'echo get_option("siteurl");' )

local_db = get_wordpress_data(local)
remote_db = get_wordpress_data(remote)

# Some extra options besides the MYSQL info
remote_db['ssh_user'] = config.get('webfaction-ssh', 'user')
remote_db['ssh_domain'] = config.get('webfaction-ssh', 'domain')

# The strings we'll use in the migration command - inspired by http://www.rogerobeid.com/2011/02/06/mysqldump-over-ssh/
local_sql = 'mysqldump -u %(user)s --password=%(pass)s %(db)s' % local_db
remote_sql = 'ssh %(ssh_user)s@%(ssh_domain)s -C "mysql -u %(user)s --password=%(pass)s -D %(db)s"' % remote_db

# This is the file we're going to move and replace wp-content with
local.c('mkdir wp-deploy')

# Moving the theme files
local.c('mkdir wp-deploy/themes')
theme_info = {'theme': wordpress_command(local,'echo get_option("current_theme"); ') }
local.c('cp -R wp-content/themes/%(theme)s wp-deploy/themes/%(theme)s' % theme_info)

# Moving the plugin files
plugins = wordpress_command(local,'echo implode(",", get_option("active_plugins")); ').split(',')
local.c('mkdir wp-deploy/plugins/')

for plugin in plugins:
    plugin_move =  {'plugin_dir': plugin.split('/')[0] }
    plugin_move['local_plugin'] = 'wp-content/plugins/%(plugin_dir)s' % plugin_move

    local.c('cp -R %(local_plugin)s wp-deploy/plugins' % plugin_move )

# Moving the uploads
uploads = wordpress_command(local,'$query = get_posts( array("post_type" => "attachment","post_status" => "any" )); echo implode(", ", array_map( function ($el) { return $el->guid; }, $query) );' ).split(',')
local.c('mkdir wp-deploy/uploads/')

for upload in uploads:
    upload_clean = upload.split('wp-content/uploads/')

    if len(upload_clean) > 1:
        upload_clean = upload_clean[0]

        upload_info = {}
        upload_info['year'] = upload_clean.split('/')[0]
        upload_info['month'] = upload_clean.split('/')[1]
        upload_info['file'] = upload_clean.split('/')[2]
        upload_info['filename'] = upload_info['file'].split('.')[0]

        local.c('mkdir wp-deploy/uploads/%(year)s' % upload_info )
        local.c('mkdir wp-deploy/uploads/%(year)s/%(month)s' % upload_info )

        upload_info['dir'] = 'wp-deploy/uploads/%(year)s/%(month)s/' % upload_info

        local.c('cp wp-content/uploads/%(year)s/%(month)s/%(filename)s* %(dir)s' % upload_info )


# Running the commands - this will only work if you've got a SSH key exchanged
scp_info = remote_db
scp_info['remote_directory'] = remote_directory
scp_command = 'scp -r wp-deploy/* %(ssh_user)s@%(ssh_domain)s:%(remote_directory)s/wp-content/' % scp_info

local.c(scp_command) # Move wp-deploy folder
local.c('rm -R wp-deploy') # Removing it

print 'Moved theme %(theme)s' % theme_info
for plugin in plugins:
    print 'Moved plugin %s' % plugin.split('/')[0]
print 'Moved all %d uploads' % len(uploads)

local.c( ''.join( [local_sql,' | ',remote_sql] ) ) # Move DB
print 'Moved and installed db'

# Updating the remote site's URLs
wordpress_command(remote, 'update_option("siteurl","%(url)s"); update_option("home","%(url)s");' % {'url':remote_url} )

# Replacing all mention of local_url in the post content with the remote url
fix_content = ''.join( [ "UPDATE `wp_posts` SET `post_content` = REPLACE(`post_content`, \"",local_url,"\",\"",remote_url,"\") WHERE `post_content` LIKE(\"%",local_url,"%\")" ] )
sql_prefix = 'mysql -u %(user)s --password=%(pass)s -D %(db)s' % remote_db
remote.c(sql_prefix+" -e '"+fix_content+"'")
# TODO: This for widgets and other wp_options (like theme files) too. Not sure how to do this as all the data is serialized

print "WordPress has been deployed"

