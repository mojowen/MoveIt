import xmlrpclib, json


class WebFaction:

    base_domain = 'scottduncombe.com'
    ip_address = '75.126.24.81'
    base_directory = None
    wordpress_install = None
    
    def __init__(self, username,password,base_domain=None):
        
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        self.session_id, self.account = self.server.login(username, password)

        if base_domain is not None:
            self.base_domain = base_domain

    def list_apps(self):
        print self.server.list_apps( self.session_id)
    
    def strip_wp_grep(self,result):
        if type(result) is list:
            result = result[0]

        result = result.split(", '")[1]
        result = result.split("'")[0]
        return result

    
    def create_site(self,name,domain=None):
        domains = [ name+"."+self.base_domain ]
        
        # If we pass a domain - then create a domain
        if domain is not None:
            domains.append(domain)
            domains.append('www.'+domain)
            self.server.create_domain(self.session_id, domain,'www')
        
        # Creating a subdomain
        self.server.create_domain(self.session_id, self.base_domain, name )
        
        #Create the web site
        self.website = self.server.create_website( self.session_id, name, self.ip_address, False, domains, [name, '/'] )
        

    def create_static(self,name,domain=None):
        
        self.wordpress_app = self.server.create_app( self.session_id, name, 'static_php54',False)
        self.create_site(name,domain)
        
    def c(self,command):
        directory = '';
        
        if self.base_directory is not None:
            directory = 'cd %s;' % self.base_directory
        
        return self.server.system( self.session_id, directory+command ).split("\n")

    def cd(self,directory):
        self.base_directory = directory
    
    
    def sql(self,command,username,password,db):
        sql = ['mysql -u',username,'--password='+password,'-D '+db,'-e',command]
        sql = " ".join(sql)
    
    def c_wordpress(self,command):
        include = 'include_once("wp-load.php"); include_once("wp-admin/includes/admin.php"); '
        
        command = include+command
        
        return self.c("php -r '%s' " % command )
    
    def get_latest_wordpress(self):
        apps = self.server.list_app_types( self.session_id )
        latest_version = 0

        for app in apps:
            
            if app['name'].find('wordpress') != -1:

                try:
                    version = int(app['name'].split('_')[1])
                except: # Sometimes has non numerical names - like "wordpress_older"
                    version = 0

                # Making sure v3.5 > v 3.4.1
                if version < 100: version = version * 10

                if version > latest_version:
                    latest_version = version
                    self.wordpress_install = app['name']

    def create_wordpress(self,name,domain=None,admin=False,new_user=False):
        
        if self.wordpress_install is None: self.get_latest_wordpress()
        
        self.wordpress_app = self.server.create_app( self.session_id, name, self.wordpress_install,True)
                
        self.create_site(name,domain)
                
        self.cd( '~/webapps/%s/' % name )
        
        self.c_wordpress('update_option("siteurl","http://'+name+"."+self.base_domain+'"); update_option("home","http://'+name+"."+self.base_domain+'");' )


        # Do something about permalinks
        # Do something about visiability to search engines
        
        # - Update admin email / password if requested
        if admin:
            update_user = 'wp_update_user( array ("ID" => 1, "user_email" => "'+admin["email"]+'") ); wp_set_password("'+admin["password"]+'",1);'
            self.c_wordpress(update_user)

        # TO DO:
        # - them as a new user (usersname, email, password as random, md5 a password reset into user_activation_key and then give them a link to login) - see wp-login.php
        # if new_user:
        #     create_new_user = 'wp_create_user( '+new_user["username"]+', '+new_user["password"]+', '+new_user["email"]+' );'
        # - TURN OFF no indexing for new sites
        # - "ln -s usefulplugins" and then add them to wp
        # - install Jolokia? maybe... 'cp -R ~/shared/BusPress/Jolokia wp-content/themes/jolokia'

        # Don't need this yet, can just do everything through WordPress
        # password = self.strip_wp_grep( self.c('grep DB_PASSWORD wp-config.php' ) )
        # username = self.strip_wp_grep( self.c('grep DB_USER wp-config.php' ) )

    def setup_googleapps(self,domain):
        mx_records = [
            ['aspmx.l.google.com',1],
            ['alt1.aspmx.l.google.com',5],
            ['alt2.aspmx.l.google.com',5],
            ['aspmx2.googlemail.com',20],
            ['aspmx3.googlemail.com',20]
        ]
        
        for mx_record in mx_records:
            self.server.create_dns_override( self.session_id, 
                domain,
                '', # An IP Address
                '', # CNAME
                mx_record[0],
                mx_record[1],
                ''
            )
        dns_overrides = ['sites','calendar','docs','mail']
        
        for override in dns_overrides:
            subdomain = override+'.'+domain
            self.server.create_domain(self.session_id, domain,  override)
            self.server.create_dns_override( self.session_id, 
                subdomain,
                '',
                'ghs.google.com', # CNAME
                '',
                '',
                ''
            )
        
    # API for interfacing with WebFactions email: 
    # http://docs.webfaction.com/xmlrpc-api/apiref.html#email
    def create_forward(self,forwarding_address,forward_to):
        try:
            new_email = self.server.create_email(self.session_id, forwarding_address, forward_to)
            return new_email['id']
        except xmlrpclib.Fault as err:
            error = err.faultString
            # error = error.split(":[u'")[1][:-2] Way to parse the string that's returned
            return error
    
    def update_forward(self, forwarding_address,forward_to):
        try:
            new_email = self.server.update_email(self.session_id, forwarding_address, forward_to)
            return new_email['id']
        except xmlrpclib.Fault as err:
            error = err.faultString
            return error

    def delete_forward(self, forwarding_address):
        return self.server.delete_email(self.session_id, forwarding_address)
