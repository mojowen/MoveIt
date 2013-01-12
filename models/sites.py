class Site:

    def __init__(self,args):
        args = args.split("\t")

        self.name = args[0]
        self.domain = args[1]

        self.bluehost_directory = '~/public_html/'+args[2]
        self.bluehost_db = args[3]

        self.webfaction_directory = '~/webapps/'+self.name+'/'
    
    def strip_wp_grep(self,result):
        result = result[0]
        result = result.split(", '")[1]
        result = result.split("'")[0]
        return result
    
    def backup_bluehost(self,bluehost):
        bluehost.cd( self.bluehost_directory )
        
        # Getting the password info
        self.bluehost_mysql_password = self.strip_wp_grep( bluehost.c('grep "DB_PASSWORD" wp-config.php') )
        self.bluehost_mysql_username = self.strip_wp_grep( bluehost.c('grep "DB_USER" wp-config.php') )
        
        # Dumping the SQL
        sql = ['mysqldump -u ',self.bluehost_mysql_username,' --password='+self.bluehost_mysql_password,self.bluehost_mysql_username,' > wp-content/db.sql']
        sql = " ".join(sql)
        bluehost.c(sql)
        
        # Backing wp-content all up into tar.bz
        bluehost.c('tar -jcvf backup.tar.bz2 wp-content')
        