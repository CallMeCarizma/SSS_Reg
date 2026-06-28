from django.contrib import admin
from .models import (
    Contractor,
    Employee,
    SiteObject,
    Document,
    DocumentAttachment,
    Equipment,
    ObjectRegistration,
    ObjectEquipment,
)


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "inn", "address")
    list_filter = ("type",)
    search_fields = ("name", "inn", "address")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone")
    search_fields = ("full_name", "email", "phone")


@admin.register(SiteObject)
class SiteObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "is_opo", "address", "contractor", "responsible")
    list_filter = ("is_opo", "status")
    search_fields = ("name", "address", "contractor__name", "responsible__full_name")


class DocumentAttachmentInline(admin.TabularInline):
    model = DocumentAttachment
    extra = 1


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "doc_type", "title", "number", "doc_date", "object")
    list_filter = ("doc_type", "doc_date")
    search_fields = ("title", "number")


@admin.register(DocumentAttachment)
class DocumentAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("document__title", "file")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "name", "checking_frequency", "verification_date")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(ObjectRegistration)
class ObjectRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "object", "reg_number", "issued_at", "is_active")
    list_filter = ("is_active", "issued_at")
    search_fields = ("reg_number",)


@admin.register(ObjectEquipment)
class ObjectEquipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "object", "equipment")
    search_fields = ("object__name", "equipment__name")