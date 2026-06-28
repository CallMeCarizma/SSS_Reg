from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0005_alter_contractor_options_contractor_contact_persons_and_more'),
    ]

    operations = [
        migrations.RemoveField(model_name='siteobject', name='contractor'),
        migrations.RemoveField(model_name='siteobject', name='responsible_from_builder'),
        migrations.RemoveField(model_name='siteobject', name='responsible_from_client'),
        migrations.AddField(
            model_name='siteobject',
            name='full_name',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='Полное наименование'),
        ),
        migrations.AddField(
            model_name='siteobject',
            name='contact_person',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Контактное лицо'),
        ),
        migrations.AddField(
            model_name='siteobject',
            name='responsible',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Ответственный'),
        ),
        migrations.AddField(
            model_name='siteobject',
            name='inn',
            field=models.CharField(blank=True, default='', max_length=12, verbose_name='ИНН'),
        ),
        migrations.AddField(
            model_name='siteobject',
            name='ogrn',
            field=models.CharField(blank=True, default='', max_length=15, verbose_name='ОГРН'),
        ),
        migrations.AddField(
            model_name='siteobject',
            name='kpp',
            field=models.CharField(blank=True, default='', max_length=9, verbose_name='КПП'),
        ),
        migrations.AddField(
            model_name='siteobject',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Договор подписан'),
                    ('invalid', 'Договор не действителен'),
                    ('delete', 'На удаление'),
                ],
                default='active',
                max_length=20,
                verbose_name='Состояние',
            ),
        ),
        migrations.AlterField(
            model_name='siteobject',
            name='address',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Адрес'),
        ),
    ]
