class Site:

    def __init__(self,args):
        args = args.split("\t")

        self.name = args[0]
        self.domain = args[1]

        self.bluehost_directory = '~/public_html/'+args[2]
        self.bluehost_db = args[3]

        self.webfaction_directory = '~/webapps/'+self.name+'/'

        try:
            self.buspress = args[4] is 'T'
        except IndexError:
            self.buspress = False

        try:
            self.google_apps = args[5] == 'Google'
        except IndexError:
            self.google_apps = False
        
        print self.purple(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")+' IMPORTING '+self.name+self.purple("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        
    def purple(self,message):
        return "\033[01;34m"+message+"\033[00m"

    def strip_wp_grep(self,result):
        result = result[0]
        result = result.split(", '")[1]
        result = result.split("'")[0]
        return result
    
    def backup_bluehost(self,bluehost):
        
        print self.purple(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")+' STEP 1'+self.purple("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        
        bluehost.cd( self.bluehost_directory )
        
        # Getting the password info
        self.bluehost_mysql_password = self.strip_wp_grep( bluehost.c('grep "DB_PASSWORD" wp-config.php') )
        self.bluehost_mysql_username = self.strip_wp_grep( bluehost.c('grep "DB_USER" wp-config.php') )
        
        # Dumping the SQL
        sql = ['mysqldump -u ',self.bluehost_mysql_username,' --password='+self.bluehost_mysql_password,self.bluehost_mysql_username,' > wp-content/db.sql']
        sql = " ".join(sql)
        bluehost.c(sql)

    def setup_webfaction_site(self,webfaction_api):
        
        print self.purple(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")+' STEP 2'+self.purple("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        
        webfaction_api.create_wordpress(self.name,self.domain)
        
        if self.google_apps:
            webfaction_api.setup_googleapps(self.domain)
            
    def webfaction_backup(self,webfaction,bluehost,ssh_connection):
        
        print self.purple(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")+' STEP 3'+self.purple("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        
        bluehost.cd(self.bluehost_directory)
        webfaction.cd(self.webfaction_directory)
        
        # First - move the package over to webfactoin
        webfaction.p('rm -r wp-content')                
        bluehost.c('scp -r wp-content '+ssh_connection+':'+self.webfaction_directory)
        
        if self.buspress: # Taking care of BusPress shared code
            webfaction.c('rm -R wp-content/themes/*olokia/custom')
            webfaction.c('cd wp-content/themes/*olokia; ln -s ~/shared/BusPress/custom')
            
        self.webfaction_mysql_password = self.strip_wp_grep( webfaction.c('grep "DB_PASSWORD" wp-config.php') )
        self.webfaction_mysql_username = self.strip_wp_grep( webfaction.c('grep "DB_USER" wp-config.php') )
        
        # Importing the new DB
        sql = ['mysql -u',self.webfaction_mysql_username,'--password='+self.webfaction_mysql_password,'-D '+self.webfaction_mysql_username,'< wp-content/db.sql']
        sql = " ".join(sql)
        webfaction.c(sql)
        
        # Fixing the domain to work with the subdomain
        fix_domain = ['mysql -u',self.webfaction_mysql_username,'--password='+self.webfaction_mysql_password,'-D '+self.webfaction_mysql_username,'-e','"UPDATE wp_options SET option_value = \'http://'+self.name+'.scottduncombe.com\' WHERE option_name IN(\'siteurl\',\'home\');"']
        fix_domain = ' '.join(fix_domain)
        webfaction.c(fix_domain)
        
    def cleanup(self,webfaction,bluehost):
        bluehost.c('rm wp-content/db.sql')
        webfaction.c('rm wp-content/db.sql')
        
        print self.purple(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")+' DONE !!! '+self.purple("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        