# Generated by Django 3.2.3 on 2021-06-06 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_sitedata_api_keys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='isProcess',
            field=models.IntegerField(default=0),
        ),
    ]