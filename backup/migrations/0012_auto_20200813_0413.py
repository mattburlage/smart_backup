# Generated by Django 3.1 on 2020-08-13 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0011_backupentry_source'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='password',
            new_name='old_password',
        ),
    ]
