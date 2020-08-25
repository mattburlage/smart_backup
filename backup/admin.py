from django.contrib import admin

from backup.models import BackupEntry, Campaign, DatabaseType, AppSetting, CampaignField, CampaignFieldOption
from backup.tasks import schedule_backup


class CampaignFieldInline(admin.TabularInline):
    model = CampaignField
    can_delete = False
    fields = ['value']
    extra = 0

    def has_add_permission(self, request, obj):
        return False


class CampaignFieldOptionInline(admin.TabularInline):
    model = CampaignFieldOption


class DatabaseTypeAdmin(admin.ModelAdmin):
    inlines = [
        CampaignFieldOptionInline,
    ]


class CampaignAdmin(admin.ModelAdmin):
    inlines = [
        CampaignFieldInline,
    ]

    def schedule_backup(self, request, queryset):

        rows_updated = 0
        for item in queryset:
            schedule_backup(item.pk)
            rows_updated += 1

        if rows_updated == 1:
            message_bit = "1 campaign scheduled."
        else:
            message_bit = f"{rows_updated} campaigns scheduled."

        self.message_user(request, message_bit)

    def activate(self, request, queryset):

        rows_updated = 0
        for item in queryset:
            item.active = True
            item.save()
            rows_updated += 1

        if rows_updated == 1:
            message_bit = "1 campaign activated."
        else:
            message_bit = f"{rows_updated} campaigns activated."

        self.message_user(request, message_bit)

    def deactivate(self, request, queryset):

        rows_updated = 0
        for item in queryset:
            item.active = False
            item.save()
            rows_updated += 1

        if rows_updated == 1:
            message_bit = "1 campaign activated."
        else:
            message_bit = f"{rows_updated} campaigns activated."

        self.message_user(request, message_bit)

    schedule_backup.short_description = "Initiate Backup(s)"
    activate.short_description = "Activate Campaign(s)"
    deactivate.short_description = "Deactivate Campaign(s)"
    actions = [schedule_backup, activate, deactivate]


admin.site.register(BackupEntry)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(DatabaseType, DatabaseTypeAdmin)
admin.site.register(AppSetting)

admin.site.site_header = 'Smart Backup Admin'


