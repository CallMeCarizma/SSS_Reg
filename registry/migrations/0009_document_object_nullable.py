from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0008_equipment_checking_frequency_integer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='object',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='registry.siteobject',
                verbose_name='Объект',
            ),
        ),
    ]
