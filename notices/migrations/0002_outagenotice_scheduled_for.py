# Generated by Django 2.2.4 on 2019-08-26 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='outagenotice',
            name='scheduled_for',
            field=models.DateTimeField(null=True),
        ),
    ]
