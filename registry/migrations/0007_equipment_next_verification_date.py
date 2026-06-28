from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0006_update_siteobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='next_verification_date',
            field=models.DateField(blank=True, null=True, verbose_name='Следующая поверка'),
        ),
    ]
