# Generated by Django 3.1.7 on 2021-07-17 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urbanshef', '0010_checklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='chef',
            name='status',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
