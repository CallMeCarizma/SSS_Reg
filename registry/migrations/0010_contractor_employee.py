from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0009_document_object_nullable'),
    ]

    operations = [
        # Contractor: добавить новые поля
        migrations.AddField(
            model_name='contractor',
            name='full_name',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='Полное наименование'),
        ),
        migrations.AddField(
            model_name='contractor',
            name='address',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='contractor',
            name='note',
            field=models.TextField(blank=True, default='', verbose_name='Заметка'),
        ),
        # Contractor: изменить choices типа
        migrations.AlterField(
            model_name='contractor',
            name='type',
            field=models.CharField(
                choices=[('individual', 'Физическое лицо'), ('legal', 'Юридическое лицо')],
                default='legal', max_length=20, verbose_name='Тип',
            ),
        ),
        # Contractor: удалить старые поля
        migrations.RemoveField(model_name='contractor', name='phone'),
        migrations.RemoveField(model_name='contractor', name='email'),
        migrations.RemoveField(model_name='contractor', name='contact_persons'),
        # Contractor: Meta
        migrations.AlterModelOptions(
            name='contractor',
            options={'ordering': ['name'], 'verbose_name': 'Контрагент', 'verbose_name_plural': 'Контрагенты'},
        ),
        # Employee: новая модель
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, default='', max_length=50, verbose_name='Телефон')),
                ('passport_data', models.TextField(blank=True, default='', verbose_name='Паспортные данные')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
                'ordering': ['full_name'],
            },
        ),
    ]
