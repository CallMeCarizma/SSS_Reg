from django.db import models


class Contractor(models.Model):
    TYPE_CHOICES = [
        ("individual", "Физическое лицо"),
        ("legal", "Юридическое лицо"),
    ]

    name = models.CharField("Наименование", max_length=255)
    full_name = models.CharField("Полное наименование", max_length=512, blank=True, default="")
    type = models.CharField("Тип", max_length=20, choices=TYPE_CHOICES, default="legal")
    inn = models.CharField("ИНН", max_length=12, blank=True, default="")
    kpp = models.CharField("КПП", max_length=9, blank=True, default="")
    ogrn = models.CharField("ОГРН", max_length=15, blank=True, default="")
    address = models.CharField("Адрес", max_length=512, blank=True, default="")
    note = models.TextField("Заметка", blank=True, default="")

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    full_name = models.CharField("ФИО", max_length=255)
    email = models.EmailField("Email", blank=True, default="")
    phone = models.CharField("Телефон", max_length=50, blank=True, default="")
    passport_data = models.TextField("Паспортные данные", blank=True, default="")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class SiteObject(models.Model):
    STATUS_CHOICES = [
        ('active', 'Договор подписан'),
        ('invalid', 'Договор не действителен'),
        ('delete', 'На удаление'),
    ]

    is_opo = models.BooleanField('ОПО', default=False)
    name = models.CharField('Наименование', max_length=255)
    full_name = models.CharField('Полное наименование', max_length=512, blank=True, default='')
    address = models.CharField('Адрес', max_length=255, blank=True, default='')
    contractor = models.ForeignKey(
        'Contractor', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='site_objects', verbose_name='Контрагент',
    )
    responsible = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='site_objects', verbose_name='Ответственный',
    )
    status = models.CharField('Состояние', max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Equipment(models.Model):
    TYPE_CHOICES = [
        ('meter', 'Прибор'),
        ('sensor', 'Датчик'),
        ('boiler', 'Котел'),
        ('valve', 'Клапан'),
        ('other', 'Прочее'),
    ]
    type = models.CharField('Тип', max_length=32, choices=TYPE_CHOICES, default='other')
    name = models.CharField('Наименование', max_length=255)
    checking_frequency = models.PositiveIntegerField('Периодичность поверки (дней)', null=True, blank=True)
    verification_date = models.DateField('Дата последней поверки', null=True, blank=True)
    next_verification_date = models.DateField('Следующая поверка', null=True, blank=True)
    passport_scan = models.FileField('Скан паспорта', upload_to='equipment_passports/', blank=True)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def verification_warning(self):
        if not self.next_verification_date:
            return ''
        from datetime import date
        days = (self.next_verification_date - date.today()).days
        if days <= 7:
            return 'warn-red'
        if days <= 15:
            return 'warn-orange'
        if days <= 30:
            return 'warn-yellow'
        return ''


class ObjectEquipment(models.Model):
    object = models.ForeignKey('SiteObject', on_delete=models.CASCADE, verbose_name='Объект')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name='Оборудование')

    class Meta:
        verbose_name = 'Оборудование объекта'
        verbose_name_plural = 'Оборудование объектов'
        unique_together = ('object', 'equipment')

    def __str__(self):
        return f'{self.object} — {self.equipment}'


class ObjectRegistration(models.Model):
    reg_number = models.CharField('Регистрационный номер', max_length=100)
    issued_at = models.DateField('Дата выдачи', null=True, blank=True)
    is_active = models.BooleanField('Действует', default=True)
    object = models.ForeignKey(
        SiteObject,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Объект'
    )

    class Meta:
        verbose_name = 'Регистрация объекта'
        verbose_name_plural = 'Регистрации объектов'
        ordering = ['-issued_at', 'reg_number']

    def __str__(self):
        return self.reg_number


class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ("contract", "Договор"),
        ("act", "Акт"),
        ("passport", "Паспорт"),
        ("certificate", "Сертификат"),
        ("protocol", "Протокол"),
        ("other", "Прочее"),
    ]

    object = models.ForeignKey(
        SiteObject,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Объект",
        null=True,
        blank=True,
    )
    doc_type = models.CharField("Тип документа", max_length=32, choices=DOC_TYPE_CHOICES, default="other")
    title = models.CharField("Название документа", max_length=255)
    number = models.CharField("Номер", max_length=100, blank=True)
    doc_date = models.DateField("Дата документа", null=True, blank=True)

    def __str__(self):
        if self.number:
            return f"{self.title} №{self.number}"
        return self.title


class DocumentAttachment(models.Model):
    document = models.ForeignKey(
        "Document",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Документ",
    )
    file = models.FileField("Файл", upload_to="documents/")
    uploaded_at = models.DateTimeField("Дата загрузки", auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.file.name.split("/")[-1]