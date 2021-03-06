# Generated by Django 2.2.4 on 2019-09-21 04:36

from django.db import migrations


def set_message_type(apps, schema_editor):
    """Assigns message type based on subject line."""
    TransactionalEmail = apps.get_model('email_alerts.TransactionalEmail')
    for item in TransactionalEmail.objects.filter(message_type__isnull=True):
        subject = item.subject_line.lower()
        if 'confirm' in subject:
            item.message_type = 'confirm'
        elif 'welcome' in subject:
            item.message_type = 'welcome'
        elif 'unsubscribe from' in subject:
            item.message_type = 'optout'
        elif 'successfully unsubscribed' in subject:
            item.message_type = 'goodbye'
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('email_alerts', '0007_transactionalemail_message_type'),
    ]

    operations = [
        migrations.RunPython(set_message_type)
    ]
