from django import forms
from .models import (
    Contractor,
    Employee,
    SiteObject,
    Document,
    Equipment,
    ObjectRegistration,
    ObjectEquipment,
    DocumentAttachment,
)


class DateInput(forms.DateInput):
    input_type = "date"


class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ["name", "full_name", "type", "inn", "kpp", "ogrn", "address", "contact_person", "phone", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3})}


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["full_name", "email", "phone", "passport_data"]
        widgets = {"passport_data": forms.Textarea(attrs={"rows": 3})}


class SiteObjectForm(forms.ModelForm):
    class Meta:
        model = SiteObject
        fields = ["name", "full_name", "address", "contractor", "responsible", "status", "is_opo"]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_type", "title", "number", "doc_date", "object"]
        labels = {
            "object": "Привязать к объекту",
        }
        widgets = {
            "doc_date": DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['object'].empty_label = "— Не привязывать —"
        self.fields['object'].required = False


class MultipleFileInput(forms.FileInput):
    """FileInput с поддержкой multiple — обходит проверку Django 6."""
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['multiple'] = True
        return attrs


class DocumentCreateForm(DocumentForm):
    attachment = forms.FileField(
        required=False,
        label='Вложения',
        widget=MultipleFileInput(),
    )


class DocumentAttachmentForm(forms.ModelForm):
    class Meta:
        model = DocumentAttachment
        fields = ["file"]


class EquipmentForm(forms.ModelForm):
    bind_object = forms.ModelChoiceField(
        queryset=SiteObject.objects.all().order_by('name'),
        required=False,
        label='Привязать к объекту',
        empty_label='— Не привязывать —',
    )

    class Meta:
        model = Equipment
        fields = [
            "type",
            "name",
            "checking_frequency",
            "verification_date",
            "passport_scan",
        ]
        widgets = {
            "verification_date": DateInput(),
        }


class ObjectRegistrationForm(forms.ModelForm):
    class Meta:
        model = ObjectRegistration
        fields = "__all__"
        widgets = {
            "issued_at": DateInput(),
        }


class ObjectEquipmentForm(forms.ModelForm):
    class Meta:
        model = ObjectEquipment
        fields = "__all__"