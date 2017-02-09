import xmlrpclib, json, time


class WebFaction:

    base_domain = 'scottduncombe.com'
    base_account = 'mojowen'
    ip_address = '75.126.24.81'
    base_directory = None
    wordpress_install = None
    default_wordpress_admin = False

    def help(self):
        print self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '''Commands:
\tSITES:
\t\t- list_apps
\t\t- create_site name,domain=None
\t\t- create_static name,doman=None
\t\t- create_wordpress name, domain=None
\t\t- create_buspress name, domain
\t\t- setup_googleapps domain
\tUSERS:
\t\t- list_users
\t\t- create_user name, password
\t\t- assign_app app, user
\t\t- create_forward forwarding_address, forward_to
\t\t- update_forward forwarding_address, forward_to
        '''

    def __init__(self, username,password,base_domain=None):

        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        self.session_id, self.account = self.server.login(username, password)

        if base_domain is not None:
            self.base_domain = base_domain

    def list_apps(self):
        apps = self.server.list_apps( self.session_id)
        for app in apps:
            print "%r" % app

    def strip_wp_grep(self,result):
        if type(result) is list:
            result = result[0]

        result = result.split(", '")[1]
        result = result.split("'")[0]
        return result


    def create_site(self,name,domain=None):
        name = name.replace('_','') # Subdomains can't have underscore

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
                self.wordpress_install = app['name']

        return self.wordpress_install

    def list_users(self):
        users = self.server.list_users( self.session_id)
        for user in users:
            print "%r" % user
    def create_user(self,name,password):
        self.server.create_user( self.session_id, name,'bash',['mojowen'] )

        self.server.change_user_password( self.session_id, name, password)

        time.sleep(10) # Hang out for a sec till the password is set for the SSH account

        # Setting up the user account
        from models.ssh import SSH
        user = SSH(self.base_domain, name, password)
        user.c('chmod 771 .')
        user.c('mkdir webapps')
        user.c('setfacl -R -m d:u:'+self.base_account+':rwx .')
        user.close()

        self.c('setfacl -m u:%s:--- $HOME/webapps/*' % name)

    def assign_app(self,app,user):

        project_dir = '$HOME/webapps/'+app

        self.cd(project_dir)
        self.c('setfacl -R -m u:'+user+':rwx ' +project_dir) # This command grants the other user read, write, and execute access to all files and directories within the application.
        self.c('setfacl -R -m d:u:'+user+':rwx ' +project_dir ) #  This command makes all new files in the application directory and its subdirectories have the same permissions by default.
        self.c('chmod -R g+s '+project_dir) # can change things
        self.c('setfacl -R -m d:u:'+self.base_account+':rwx '+project_dir) # This command allows the primary user to continue to have full access to files, even if they're created by the secondary user.

        self.cd('/home/'+user+'/webapps/')
        self.c('ln -s '+project_dir+' %s '%app) # moving in a project

    def set_default_wordpress_admin(self,email, password, username='admin'):
        self.default_wordpress_admin = { "email": email, "password": password, 'username': username }

    def create_wordpress(self,name,domain=None,admin=False,new_user=False):

        if self.wordpress_install is None: self.get_latest_wordpress()

        self.wordpress_app = self.server.create_app( self.session_id, name, self.wordpress_install,True)

        self.create_site(name,domain)

        self.cd( '~/webapps/%s/' % name )

        self.c_wordpress('update_option("siteurl","http://'+name+"."+self.base_domain+'"); update_option("home","http://'+name+"."+self.base_domain+'");' )


        # Do something about permalinks
        # Do something about visiability to search engines

        # - Update admin email / password if requested
        if not admin and self.default_wordpress_admin:
            admin = self.default_wordpress_admin

        if admin:
            update_user = '$wpdb->update($wpdb->users, array ("user_login" => "%s", "user_email" => "%s"), array( "ID" => 1 ) ); wp_set_password("%s",1);' % (admin["username"], admin["email"], admin["password"])
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

    def create_buspress(self, name, domain=None):
        self.create_wordpress(name, domain)
        self.assign_app(name, 'bus')

        self.c('cp -r ~/shared/BusPress/jolokia ~/webapps/%s/wp-content/themes' % name)
        self.c('ln -s ~/shared/ng-forms ~/webapps/%s/wp-content/plugins/ng-forms' % name)

        if domain:
            self.setup_googleapps(domain, '_spfprod.ngpvan.com')
            # Set up TXT Record for NGP VAN SPF
            ngp_domain = 'ngpweb3._domainkey'
            self.server.create_domain(self.session_id, domain, ngp_domain)
            ngp_domain += '.%s' % ngp_domain
            key = ('v=DKIM1; k=rsa; n=1024; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCB'
                   'iQKBgQD+FZRWRvxNzHH8gasWTJi4+bWRyDSMgEI7XOwAzUyrrvwz4QZ4lD'
                   'tOwQVAmkqxUiyf5YkufT6+5h15wmR0f82JwqwT1vMjOUNS/Kausds5aBJi'
                   'u2GFsIFrwXBUFf2Hp81yRzWQ56XoP+QTYJDk7Q3NRRGg17QfOZSDfPZCMI'
                   'CFVwIDAQAB')
            self.server.create_dns_override(self.session_id, ngp_domain, '', '', '', '', key)


    def setup_googleapps(self,domain, other_spf_domains=None):
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
            self.server.create_dns_override(self.session_id,
                subdomain, '', 'ghs.google.com', # CNAME
                '','', ''
            )

        other_spf_domains = 'include:%s' % other_spf_domains if other_spf_domains else ''

        self.server.create_dns_override(
            self.session_id,
            domain,
            '', '', '', '',
            'v=spf1 include:_spf.google.com %s~all' % other_spf_domains)

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

    def bulk_create_forwards(self,block):
        blocks = block.split("\n")

        for block in blocks:
            forward = block.split("\t")
            self.create_forward( forward[0], forward[1] )
            print "forwarding "+forward[0]+' to '+forward[1]
