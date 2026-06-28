import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0010_contractor_employee'),
    ]

    operations = [
        # Удаляем старые текстовые поля
        migrations.RemoveField(model_name='siteobject', name='contact_person'),
        migrations.RemoveField(model_name='siteobject', name='inn'),
        migrations.RemoveField(model_name='siteobject', name='ogrn'),
        migrations.RemoveField(model_name='siteobject', name='kpp'),
        # Заменяем responsible (CharField) на FK к Employee
        migrations.RemoveField(model_name='siteobject', name='responsible'),
        migrations.AddField(
            model_name='siteobject',
            name='responsible',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='site_objects', to='registry.employee',
                verbose_name='Ответственный',
            ),
        ),
        # Добавляем contractor FK
        migrations.AddField(
            model_name='siteobject',
            name='contractor',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='site_objects', to='registry.contractor',
                verbose_name='Контрагент',
            ),
        ),
    ]
