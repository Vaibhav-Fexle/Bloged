# Generated by Django 3.2.3 on 2021-06-03 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_alter_blogger_user_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogger',
            name='user_pic',
            field=models.ImageField(default='/user/profil.png', upload_to='user/'),
        ),
    ]
