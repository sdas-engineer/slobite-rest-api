# Generated by Django 3.1.7 on 2021-05-09 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urbanshef', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='service_charge',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='meal',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='A 20% tax will be automatically added to the price', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_charge',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='sub_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]