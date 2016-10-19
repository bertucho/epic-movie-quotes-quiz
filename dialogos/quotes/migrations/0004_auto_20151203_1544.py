# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0003_auto_20151023_2008'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='total_votes',
            new_name='votes',
        ),
        migrations.AddField(
            model_name='movie',
            name='original_title',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]
