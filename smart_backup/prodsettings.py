from smart_backup.settings import *

# DEBUG = False

# SECRET_KEY = os.environ.get('DJANGO_KEY')


ALLOWED_HOSTS = [
    'smartbackup.hallcounty.org'
]

FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', '')

