# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='khachhang',
            index=models.Index(fields=['PhoneNumber'], name='customers_kh_phone_idx'),
        ),
        migrations.AddIndex(
            model_name='khachhang',
            index=models.Index(fields=['Email'], name='customers_kh_email_idx'),
        ),
        migrations.AddIndex(
            model_name='khachhang',
            index=models.Index(fields=['LoyaltyPoints'], name='customers_kh_points_idx'),
        ),
    ]
