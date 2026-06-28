from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0007_equipment_next_verification_date'),
    ]

    operations = [
        # Сначала разрешаем NULL, чтобы можно было очистить текстовые значения
        migrations.AlterField(
            model_name='equipment',
            name='checking_frequency',
            field=models.CharField(blank=True, null=True, max_length=100, verbose_name='Периодичность поверки'),
        ),
        # Очищаем все существующие текстовые значения
        migrations.RunSQL(
            sql="UPDATE registry_equipment SET checking_frequency = NULL",
            reverse_sql="",
        ),
        # Меняем тип на целочисленный
        migrations.AlterField(
            model_name='equipment',
            name='checking_frequency',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Периодичность поверки (дней)'),
        ),
    ]
