# Generated by Django 3.2.3 on 2021-06-20 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20210620_1922'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='null', max_length=30)),
                ('work', models.CharField(default='null', max_length=30)),
                ('github', models.CharField(default='null', max_length=30)),
                ('codeforces', models.CharField(default='null', max_length=30)),
                ('leetcode', models.CharField(default='null', max_length=30)),
                ('atcoder', models.CharField(default='null', max_length=30)),
            ],
        ),
    ]
