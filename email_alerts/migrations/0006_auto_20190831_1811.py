# Generated by Django 2.2.4 on 2019-08-31 10:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_alerts', '0005_auto_20190831_1320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailalert',
            old_name='recipients',
            new_name='recipient',
        ),
    ]
