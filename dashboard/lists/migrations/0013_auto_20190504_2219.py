# Generated by Django 2.1.2 on 2019-05-04 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0012_auto_20180416_2345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
