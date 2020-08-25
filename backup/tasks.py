import datetime
import os
import subprocess

from background_task import background
from django.core.files import File

from backup.models import Campaign, BackupEntry, AppSetting
from smart_backup.settings import BASE_DIR


@background(schedule=5)
def schedule_backup(camp_id, source=None, keep=False):
    backup_postgres(camp_id, source=source, keep=keep)


@background(schedule=5)
def daily_tasks(camp_ids=None, manual=False):
    today = datetime.date.today()
    a_week_ago = today - datetime.timedelta(days=7)
    a_month_ago = today - datetime.timedelta(days=31)
    a_year_ago = today - datetime.timedelta(days=366)

    all_camps = Campaign.objects.filter(active=True)

    if camp_ids:
        if not isinstance(camp_ids, list):
            camp_ids = [camp_ids]

        all_camps = all_camps.filter(pk__in=camp_ids)

    # perform daily backup
    camps = all_camps.filter(backup_daily=True)

    for camp in camps:
        backup_postgres(camp.pk, source='Automated')

    # if day of week is sunday, delete
    if manual or today.weekday() == 0:
        camps = all_camps.filter(condense_weekly=True)
        for camp in camps:
            items = BackupEntry.objects.filter(campaign=camp, do_not_delete=False).order_by('-added_on')
            for item in items:
                if item.added_on < a_week_ago and len(item.week_items().exclude(pk=item.pk)) > 0:
                    items = items.exclude(pk=item.pk)
                    # item.file.delete()
                    item.delete()

    # if day of month is the 1st, delete
    if manual or today.day == 1:
        camps = all_camps.filter(condense_monthly=True)
        for camp in camps:
            items = BackupEntry.objects.filter(campaign=camp, do_not_delete=False).order_by('-added_on')
            for item in items:

                if item.added_on < a_month_ago and len(item.month_items().exclude(pk=item.pk)) > 0:
                    items = items.exclude(pk=item.pk)
                    # item.file.delete()
                    item.delete()

    # if day of month is the 1st, delete
    if manual or (today.day == 1 and today.month == 1):
        camps = all_camps.filter(condense_yearly=True)
        for camp in camps:
            items = BackupEntry.objects.filter(campaign=camp, do_not_delete=False).order_by('-added_on')
            for item in items:
                if item.added_on < a_year_ago and len(item.year_items().exclude(pk=item.pk)) > 0:
                    items = items.exclude(pk=item.pk)
                    # item.file.delete()
                    item.delete()


@background(schedule=5)
def schedule_remove(file):
    try:
        os.remove(file)
    except:
        pass


# BACKUP FUNCTIONS


def backup_postgres(camp_id, keep=False, source=None):
    camp = Campaign.objects.get(pk=camp_id)

    conn_string = f"--dbname=postgresql://{camp.user}:{camp.password}@{camp.host}/{camp.database}"

    pg_dump_path = AppSetting.get_setting('PG_DUMP_PATH')
    temp_path = os.path.join(BASE_DIR, 'temp')
    filename = "dump.backup"
    temp_file = os.path.join(temp_path, filename)

    subprocess.call([pg_dump_path, conn_string, "-Fc", f"--file={temp_file}"])

    reopen = open(temp_file, 'rb')
    new_file = File(reopen)

    new_backup = BackupEntry.objects.create(campaign_id=camp.pk, do_not_delete=keep, source=source, safe_deleted=False)
    new_backup.file.save(filename, new_file, save=True)

    schedule_remove(temp_file, schedule=120)
#
#
# def backup_mssql(camp_id, keep=False, source=None):
#     camp = Campaign.objects.get(pk=camp_id)
#
#     conn = pyodbc.connect(
#
#     )
