#!/usr/bin/python

import commands
import sys
from models import Local

def strip_wp_grep(result):
    if type(result) is list:
        result = result[0]
    result = result.split(", '")[1]
    result = result.split("'")[0]
    return result

local = Local()
local.cd('~/webapps')

directories = local.c('ls').split("\n")

for site in directories:
    try:
        local.cd('~/webapps/'+site)
        is_wordpress = local.c('ls wp-config.php') == 'wp-config.php'

        if is_wordpress:
            # Upgrade wordpress
            local.c("php ~/MoveIt/misc/upgrade_wordpress.php")

            # Upgrade plugins
            upgrade = local.c("php ~/MoveIt/misc/plugin_restore.php")

            # Upgrade themes
            upgrade = local.c("php ~/MoveIt/misc/theme_restore.php")

            print "Upgraded %s\n" % site
        else:
            print "Skipping %s\n" % site
    except:
        print "Something went wrong upgrading %s\n" % site

