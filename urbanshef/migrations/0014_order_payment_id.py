# Generated by Django 3.1.7 on 2021-07-22 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urbanshef', '0013_auto_20210721_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
