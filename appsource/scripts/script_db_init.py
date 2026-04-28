
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

django.setup()

import os
import traceback
import sys
import glob
from config import settings
from config import app_logger
from django.core.management import call_command
from mck_auth.models import User, Account, AccountUser, AccountType, AccountTypeRole


from scripts import script_fixtures_build
from scripts import script_fixtures_run
from scripts import generate_master_permission
from scripts import update_mck_role_master_permissions

log_name = "app_scripts"
logger = app_logger.createLogger(log_name)

dbengine = settings.DATABASES['default']['ENGINE']
dbname   = settings.DATABASES['default']['NAME']
dbhost   = settings.DATABASES['default']['HOST']
dbuser   = settings.DATABASES['default']['USER']
dbpass   = settings.DATABASES['default']['PASSWORD']

@app_logger.functionlogs(log="app_scripts")
def createDatabase():
    result=False
    try:
        if dbengine == "django.db.backends.sqlite3":
            import sqlite3
            logger.debug("creating database...{0}".format(dbname))        
            conn = sqlite3.connect(dbname)
            logger.debug("created database...{0}".format(dbname))
            result=True          
        if dbengine == "mysql.connector.django" or dbengine == "django.db.backends.mysql":
            import mysql.connector            
            db = mysql.connector.connect(host=dbhost,user=dbuser,passwd=dbpass)
            logger.debug("creating database...{0}".format(dbname))
            cursor = db.cursor()
            createsql = "create SCHEMA %s CHARACTER SET utf16 COLLATE utf16_general_ci"% (dbname)
            cursor.execute(createsql)
            cursor.close()
            db.close()
            logger.debug("created database...{0}".format(dbname))
            result=True
    except Exception as error:
        logger.error(traceback.format_exc())
        raise error
    return result

@app_logger.functionlogs(log="app_scripts")
def dropDatabase():
    result=False
    try:
        logger.info(dbengine)
        if dbengine == "django.db.backends.sqlite3":
            import sqlite3
            logger.debug("dropping database...{0}".format(dbname))
            if os.path.exists(dbname):
                os.remove(dbname)
                logger.debug("dropped database...{0}".format(dbname))
                result=True
            else:
                logger.info(f"Database {dbname} does not exist.")
        if dbengine == "mysql.connector.django" or dbengine == "django.db.backends.mysql":
            import mysql.connector            
            db = mysql.connector.connect(host=dbhost,user=dbuser,passwd=dbpass)
            cursor = db.cursor()
            dropsql = 'drop database %s' % (dbname)
            logger.debug(dropsql)
            logger.debug("dropping database...{0}".format(dbname))
            cursor.execute(dropsql)
            cursor.close()
            db.close()
            logger.debug("dropped database...{0}".format(dbname))
            result=True
    except Exception as error:
        logger.error(traceback.format_exc())
        raise error
    return result

@app_logger.functionlogs(log=log_name)
def run_migrations():
    result = False
    try:
        # remove migration files
        app_list = [
    app for app in settings.INSTALLED_APPS 
    if app.startswith("mck_") or app.startswith("mck_website")
]

        for apps in app_list:
            apps = apps.replace(".","/")
            migration_path = os.path.join(settings.BASE_DIR, '%s/migrations'%(apps))
            print(migration_path)
            for file in glob.glob(migration_path+"/0*.py"):
                os.remove(file)
        all_app_list = [ app for app in settings.INSTALLED_APPS if app.startswith("mck_") or app.startswith("mck_website")]
        for apps in all_app_list:
            try:
                call_command('makemigrations','--pythonpath', apps, interactive=False)
            except Exception as error:
                logger.error(traceback.format_exc())
                raise error
        result = True
    except Exception as error:
        logger.error(traceback.format_exc())
        raise error
    call_command('makemigrations', interactive=False)
    call_command('migrate', interactive=False)
    return result

@app_logger.functionlogs(log=log_name)
def create_authusers():
    superuser = User()
    superuser.is_active = True
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.username = "mck"
    superuser.mobile_number = "6379573737"
    superuser.email = "mckbytes@gmail.com"
    superuser.set_password("mckbytes321")
    superuser.first_name = "sri"
    superuser.last_name = "varam"
    superuser.save()
    return superuser

@app_logger.functionlogs(log=log_name)
def create_superuser_account(superuser):
    account_type = AccountType.objects.filter(code="mck").first()
    account = Account()
    account.account_type = account_type
    account.name = str(account_type.name) + " Account"
    account.created_by = superuser
    account.updated_by = superuser
    account.save()
    
    if not AccountUser.objects.filter(account=account, user=superuser, datamode='A').exists():
        account_user = AccountUser()
        account_user.account = account
        account_user.user = superuser
        account_user.role = AccountTypeRole.objects.filter(account_type=account.account_type).first()
        account_user.is_default_account = True
        account_user.is_current_account = True
        account_user.created_by = superuser
        account_user.updated_by = superuser
        account_user.save()

@app_logger.functionlogs(log=log_name)
def create_company_profile():
    company_user = User()
    company_user.is_active = True
    company_user.is_superuser = False
    company_user.is_staff = False
    company_user.username = "company_admin"
    company_user.mobile_number = "9940767842"
    company_user.email = "company_admin@gmail.com"
    company_user.set_password("secret@123")
    company_user.first_name = "Company"
    company_user.last_name = "Admin"
    company_user.save()

    account_type = AccountType.objects.filter(code="BUS").first()
    account = Account()
    account.account_type = account_type
    account.name = str(account_type.name) + " Account"
    account.created_by = company_user
    account.updated_by = company_user
    account.save()

    account_user = AccountUser()
    account_user.account = account
    account_user.user = company_user
    account_user.role = AccountTypeRole.objects.filter(account_type=account.account_type).first()
    account_user.is_default_account = True
    account_user.is_current_account = True
    account_user.created_by = company_user
    account_user.updated_by = company_user
    account_user.save()

    

@app_logger.functionlogs(log=log_name)
def run():
    logger.info("Starting ...")
    dropDatabase()
    createDatabase()
    run_migrations()
    superuser = create_authusers()
    script_fixtures_build.build_fixtures(app_name=None)
    script_fixtures_run.run_fixtures(app_name=None)
    create_superuser_account(superuser)
    generate_master_permission.generate_master_permission()
    update_mck_role_master_permissions.update_role_master_permission()
    create_company_profile()
    logger.info("End !!!")


def run():
    logger.info("Starting ...")
    dropDatabase()
    createDatabase()
    run_migrations()
    superuser = create_authusers()
    script_fixtures_build.build_fixtures(app_name=None)
    script_fixtures_run.run_fixtures(app_name=None)
    create_superuser_account(superuser)
    generate_master_permission.generate_master_permission()
    update_mck_role_master_permissions.update_role_master_permission()
    create_company_profile()
    logger.info("End !!!")


if __name__ == "__main__":
    run()
