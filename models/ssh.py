import paramiko, base64

class SSH:
    base_dir = None
    
    def __init__(self,host,user,password,base_dir=None):
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        
        self.client.connect(host, username=user, password=password)
        
        if base_dir is not None:
            self.cd(base_dir)

    def cd(self,dir):
        self.base_dir = dir
    
    def c(self,command):
        if self.base_dir is not None:
            command = 'cd '+self.base_dir+';'+command
            
        stdin, stdout, stderr = self.client.exec_command(command)

        error = stderr.readlines()

        if len(error) > 0:
            raise Exception(error)
        else:
            fixed = []

            for line in stdout.readlines():
                fixed.append( line.strip() )
            
            return fixed

    def p(self,command):
        result = self.c(command)

        for line in result:
            print line.strip()
        
    def close(self):
        ssh.close()