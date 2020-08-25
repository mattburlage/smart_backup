from django import forms

from backup.models import Campaign


class CampaignForm(forms.ModelForm):

    class Meta:
        model = Campaign
        fields = [
            'title', 'slug', 'db_type', 'host', 'database',
            'user', 'password',
            'active', 'backup_daily', 'condense_weekly',
            'condense_monthly', 'condense_yearly',
        ]

        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }


