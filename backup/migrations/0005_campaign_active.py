# Generated by Django 3.0.8 on 2020-07-31 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0004_auto_20200731_0059'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]