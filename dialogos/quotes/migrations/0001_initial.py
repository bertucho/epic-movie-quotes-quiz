# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('year', models.IntegerField()),
                ('imdb_score', models.DecimalField(max_digits=3, decimal_places=1)),
                ('total_votes', models.IntegerField()),
                ('posterPath', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=1024)),
                ('score', models.DecimalField(max_digits=2, decimal_places=1)),
                ('popularity_rank', models.DecimalField(max_digits=3, decimal_places=1)),
                ('level', models.IntegerField()),
                ('movie', models.ForeignKey(to='quotes.Movie')),
            ],
        ),
    ]
