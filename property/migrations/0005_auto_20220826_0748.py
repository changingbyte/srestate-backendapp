# Generated by Django 3.0 on 2022-08-26 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0004_auto_20220826_0650'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='estate',
            unique_together={('estate_type', 'estate_status', 'area', 'society', 'rent_status')},
        ),
    ]
