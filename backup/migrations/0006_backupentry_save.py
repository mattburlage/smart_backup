# Generated by Django 3.0.8 on 2020-07-31 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0005_campaign_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupentry',
            name='save',
            field=models.BooleanField(default=False),
        ),
    ]
