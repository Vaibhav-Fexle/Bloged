# Generated by Django 3.2.3 on 2021-06-04 06:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('blog', '0021_usernew'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserNew',
        ),
    ]
