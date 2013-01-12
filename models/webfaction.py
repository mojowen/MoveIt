import xmlrpclib, json

class WebFaction:

    base_domain = 'scottduncombe.com'
    ip_address = '75.126.24.81'
    
    def __init__(self, username,password):
        
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        self.session_id, self.account = self.server.login(username, password)

    def list_apps(self):
        print self.server.list_apps( self.session_id)
    
    def create_wordpress(self,name,domain=None):
        
        self.wordpress_app = self.server.create_app( self.session_id, name, 'wordpress_35',True)
        
        domains = [ name+"."+self.base_domain ]
        
        # If we pass a domain - then create a domain
        if domains is not None:
            domains.append(domain)
            self.server.create_domain(self.session_id, domain)
        
        # Creating a subdomain
        self.server.create_domain(self.session_id, self.base_domain, name )
        
        #Create the web site
        self.website = self.server.create_website( self.session_id, name, self.ip_address, False, domains, [name, '/'] )

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
