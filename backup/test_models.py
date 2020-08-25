from datetime import timedelta
from unittest import TestCase

from django.test import TestCase
from django.utils import timezone

from backup.models import Campaign, BackupEntry, DatabaseType, CampaignFieldOption, AppSetting
from backup.tasks import daily_tasks


class TestCampaign(TestCase):
    def setUp(self) -> None:
        db_type = DatabaseType.objects.create(title='Test Postgres')
        CampaignFieldOption.objects.create(
            database_type=db_type,
            key="Test Field 1"
        )
        CampaignFieldOption.objects.create(
            database_type=db_type,
            key="Test Field 2"
        )

        Campaign.objects.create(
            title="Test Campaign 1",
            slug="test-camp-1",
            active=True,
            backup_daily=False,
            condense_weekly=False,
            condense_monthly=False,
            condense_yearly=False,
            db_type=db_type,
        )

    def test_save(self):
        campaign = Campaign.objects.first()

        self.assertEqual(campaign.extra_fields.count(), 2)
        self.assertEqual(campaign.extra_fields.first().key, 'Test Field 1')
        self.assertEqual(campaign.extra_fields.last().key, 'Test Field 2')


class TestBackupEntry(TestCase):
    days_back = 700
    today = timezone.now().date()

    def setUp(self) -> None:
        campaign = Campaign.objects.create(
            title="Test Campaign 1",
            slug="test-camp-1",
            active=True,
            backup_daily=False,
            condense_weekly=False,
            condense_monthly=False,
            condense_yearly=False
        )

        monday = self.today - timedelta(days=self.today.weekday())
        cur_date = monday - timedelta(days=self.days_back)

        counter = 0
        while cur_date < timezone.now().date():
            new_backup = BackupEntry.objects.create(
                campaign=campaign,
                source='Testing',
                safe_deleted=False,
                do_not_delete=False,
            )

            new_backup.added_on = cur_date
            new_backup.save()

            counter += 1
            cur_date = cur_date + timedelta(days=1)

    def test_condense_weekly(self):
        campaign = Campaign.objects.first()
        campaign.condense_weekly = True
        campaign.save()

        daily_tasks.now(camp_ids=[campaign.pk], manual=True)

        items = BackupEntry.objects.all().order_by('-added_on')[7:]

        for backup in items:
            self.assertEqual(backup.week_items().exclude(pk=backup.pk).count(), 0)

    def test_condense_monthly(self):
        campaign = Campaign.objects.first()
        campaign.condense_monthly = True
        campaign.save()

        daily_tasks.now(camp_ids=[campaign.pk], manual=True)

        items = BackupEntry.objects.all().order_by('-added_on')[31:]

        for backup in items:
            self.assertEqual(backup.month_items().exclude(pk=backup.pk).count(), 0)

    def test_condense_yearly(self):
        campaign = Campaign.objects.first()
        campaign.condense_yearly = True
        campaign.save()

        daily_tasks.now(camp_ids=[campaign.pk], manual=True)

        items = BackupEntry.objects.all().order_by('-added_on')[366:]

        for backup in items:
            self.assertEqual(backup.year_items().exclude(pk=backup.pk).count(), 0)

    def test_do_not_delete(self):
        campaign = Campaign.objects.first()
        campaign.condense_weekly = True
        campaign.save()

        for item in BackupEntry.objects.all():
            item.do_not_delete = True
            item.save()

        pre_count = BackupEntry.objects.count()

        daily_tasks.now(camp_ids=[campaign.pk], manual=True)

        post_count = BackupEntry.objects.count()

        self.assertEqual(pre_count, post_count)


class TestAppSetting(TestCase):
    def setUp(self) -> None:
        AppSetting.objects.create(
            name='Test Setting 1',
            type="Boolean",
            bool_setting=True
        )
        AppSetting.objects.create(
            name='Test Setting 2',
            type="String",
            string_setting='This is a test',
        )
        AppSetting.objects.create(
            name='Test Setting 3',
            type="Number",
            float_setting=35
        )

    def test_get_setting(self):
        self.assertEqual(AppSetting.get_setting('Test Setting 1'), True)
        self.assertEqual(AppSetting.get_setting('Test Setting 2'), 'This is a test')
        self.assertEqual(AppSetting.get_setting('Test Setting 3'), 35)
