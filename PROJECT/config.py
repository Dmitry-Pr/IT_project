import os
import dotenv

dotenv.load_dotenv('.env')
host = os.environ['host']
user = os.environ['user']
port = 3306
passwd = os.environ['passwd']
database = os.environ['database']
ftp_login = os.environ['ftp_login']
ftp_passwd = os.environ['ftp_passwd']