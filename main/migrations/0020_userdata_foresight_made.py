# Generated by Django 3.2.3 on 2021-06-20 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20210617_0236'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='foresight_made',
            field=models.IntegerField(default=0),
        ),
    ]
