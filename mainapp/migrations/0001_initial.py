# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 03:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text1', models.CharField(max_length=200)),
                ('text2', models.CharField(max_length=200)),
                ('text3', models.CharField(max_length=200)),
                ('text4', models.CharField(max_length=200)),
                ('submit_time', models.DateTimeField(verbose_name='date published')),
                ('submitter', models.CharField(max_length=200)),
            ],
        ),
    ]