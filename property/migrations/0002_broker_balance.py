# Generated by Django 3.0 on 2022-04-08 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]