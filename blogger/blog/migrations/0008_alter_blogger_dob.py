# Generated by Django 3.2.3 on 2021-06-03 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_blogger_dob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogger',
            name='DOB',
            field=models.DateTimeField(),
        ),
    ]
