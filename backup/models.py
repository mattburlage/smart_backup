import datetime

from django.db import models
from django_cryptography.fields import encrypt

from backup.constants import TIMESTAMP_FORMAT


class AppSetting(models.Model):
    setting_type_ch = (
        ("Boolean", "Boolean"),
        ("String", "String"),
        ("Number", "Number"),
    )

    name = models.CharField(max_length=64, verbose_name="Setting Name")
    type = models.CharField(max_length=10, choices=setting_type_ch,
                            verbose_name="Setting Type", default="Boolean")
    bool_setting = models.BooleanField(verbose_name="Setting Value (Boolean)", default=False)
    string_setting = models.CharField(max_length=64, verbose_name="Setting Value (String)", null=True, blank=True)
    float_setting = models.FloatField(verbose_name="Setting Value (Number)", null=True, blank=True)
    description = models.CharField(max_length=128, verbose_name="Setting Description", null=True, blank=True)

    @staticmethod
    def get_setting(setting_name):
        return AppSetting.objects.get(name=setting_name).setting()

    class Meta:
        verbose_name = "App Setting"

    def setting(self):
        if self.type == "String":
            return self.string_setting
        elif self.type == "Boolean":
            return self.bool_setting
        elif self.type == "Number":
            return self.float_setting

    def __str__(self):
        return self.name


class DatabaseType(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title


class Campaign(models.Model):
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=32)

    db_type = models.ForeignKey(DatabaseType, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Database Type')
    host = models.CharField(max_length=255, null=True, blank=True)
    database = models.CharField(max_length=255, null=True, blank=True)
    user = models.CharField(max_length=255, null=True, blank=True)
    password = encrypt(models.CharField(max_length=255, null=True, blank=True))

    active = models.BooleanField(default=False)

    backup_daily = models.BooleanField(default=False)
    condense_weekly = models.BooleanField(default=False)
    condense_monthly = models.BooleanField(default=False)
    condense_yearly = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Campaign, self).save(*args, **kwargs)

        # Set extra fields for each database type, remove others
        if self.db_type:
            field_list = []
            for field in self.db_type.field_options.all():
                field_list.append(field.key)
                if field.key not in self.extra_fields.values_list('key', flat=True):
                    new_field = CampaignField.objects.create(
                        campaign=self,
                        key=field.key,
                        value=None,
                    )
                    self.extra_fields.add(new_field)

            for field in self.extra_fields.all():
                if field.key not in field_list:
                    field.delete()

    @property
    def total_size(self):
        size = 0
        for item in self.backups.all():
            size += item.file.size

        return size

    @property
    def last_backup_size(self):
        last_upload = self.backups.last()

        if last_upload:
            return last_upload.size
        else:
            return None

    @property
    def last_backup(self):
        return self.backups.last()

    def __str__(self):
        return self.title


def backup_path(instance, filename):
    slug = instance.campaign.slug
    camp_id = instance.campaign.pk
    timestamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)

    return f"backups/{slug}-{camp_id}/{timestamp}/{filename}"


class BackupEntry(models.Model):
    file = models.FileField(upload_to=backup_path, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='backups')
    added_on = models.DateField(auto_now_add=True)
    added_on_time = models.TimeField(auto_now_add=True)
    source = models.CharField(max_length=16, null=True, blank=True)

    do_not_delete = models.BooleanField(default=False)

    safe_deleted = models.BooleanField(default=False)

    def week_items(self):
        cur_weekday = self.added_on.weekday()
        monday = self.added_on - datetime.timedelta(days=cur_weekday)
        sunday = monday + datetime.timedelta(days=6)

        return BackupEntry.objects.filter(added_on__gte=monday, added_on__lte=sunday)

    def month_items(self):
        return BackupEntry.objects.filter(added_on__month=self.added_on.month, added_on__year=self.added_on.year)

    def year_items(self):
        return BackupEntry.objects.filter(added_on__year=self.added_on.year)

    @property
    def size(self):
        if self.file.file:
            return self.file.size
        else:
            return 0

    @property
    def added_on_dt(self):
        return datetime.datetime.combine(self.added_on, self.added_on_time)

    @property
    def day_of_week(self):
        return self.added_on.weekday()

    @property
    def day_of_month(self):
        return self.added_on.day

    @property
    def day_of_year(self):
        return int(self.added_on.strftime('%j'))

    def __str__(self):
        return f"{self.campaign.title} - {self.added_on_dt.strftime(TIMESTAMP_FORMAT)}"


class CampaignField(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='extra_fields')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.key} ({self.campaign.title})"


class CampaignFieldOption(models.Model):
    database_type = models.ForeignKey(DatabaseType, on_delete=models.CASCADE, related_name='field_options')
    key = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} ({self.database_type.title})"
