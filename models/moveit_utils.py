def strip_wp_grep(result):
    if type(result) is list:
        result = result[0]
    result = result.split(", '")[1]
    result = result.split("'")[0]
    return result

def get_wordpress_data(operator):
    
    info = {}
    
    info['pass'] = strip_wp_grep( operator.c('grep DB_PASSWORD wp-config.php') )
    info['user'] = strip_wp_grep( operator.c('grep DB_USER wp-config.php') )
    info['db'] =  strip_wp_grep( operator.c('grep DB_NAME wp-config.php') )
    
    return info
    
def wordpress_command(operator,command):
    
    include = 'include_once("wp-load.php"); include_once("wp-admin/includes/admin.php"); '
    
    command = include+command
    
    return operator.c("php -r '%s' " % command )
    