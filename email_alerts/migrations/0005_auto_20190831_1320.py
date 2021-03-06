# Generated by Django 2.2.4 on 2019-08-31 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('email_alerts', '0004_auto_20190830_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailalert',
            name='outage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_alerts', to='notices.OutageNotice'),
        ),
        migrations.RemoveField(
            model_name='emailalert',
            name='recipients',
        ),
        migrations.AddField(
            model_name='emailalert',
            name='recipients',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_alerts_received', to=settings.AUTH_USER_MODEL),
        ),
    ]
