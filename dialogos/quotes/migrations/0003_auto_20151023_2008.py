# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0002_quote_mf_visits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='popularity_rank',
            field=models.DecimalField(max_digits=6, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='quote',
            name='score',
            field=models.DecimalField(max_digits=4, decimal_places=1),
        ),
    ]
