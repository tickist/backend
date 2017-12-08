# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
# -*- coding: utf-8 -*-
from django.db import models, migrations
from commons.utils import zero_or_number

def combine_names(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Task = apps.get_model("tasks", "Task")
    for task in Task.objects.all():
        task.estimate_time_backup = zero_or_number(task.estimate_time)
        task.time_backup = zero_or_number(task.time)
        task.save()



class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_task_estimate_time_backup'),
    ]

    operations = [
        migrations.RunPython(combine_names),

    ]

