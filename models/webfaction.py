from django.conf import settings
import xmlrpclib, json

class WebFaction:

    def __init__(self, username=settings.WEBFACTION_USER,password=settings.WEBFACTION_PASSWORD):
        
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        self.session_id, self.account = self.server.login(username, password)

    def list_apps(self):
        print self.server.list_apps( self.session_id)
        
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
