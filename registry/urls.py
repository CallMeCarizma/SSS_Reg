from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("search/", views.global_search, name="global_search"),
    path("calendar/", views.equipment_calendar, name="equipment_calendar"),
path("document-attachments/<int:pk>/delete/", views.document_attachment_delete, name="document_attachment_delete"),

    path("contractors/", views.contractor_list, name="contractor_list"),
    path("contractors/create/", views.ContractorCreateView.as_view(), name="contractor_create"),
    path("contractors/<int:pk>/detail/", views.contractor_detail_json, name="contractor_detail_json"),
    path("contractors/<int:pk>/update/", views.contractor_update_json, name="contractor_update_json"),
    path("contractors/<int:pk>/edit/", views.ContractorUpdateView.as_view(), name="contractor_edit"),
    path("contractors/<int:pk>/delete/", views.ContractorDeleteView.as_view(), name="contractor_delete"),

    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.EmployeeCreateView.as_view(), name="employee_create"),
    path("employees/<int:pk>/detail/", views.employee_detail_json, name="employee_detail_json"),
    path("employees/<int:pk>/update/", views.employee_update_json, name="employee_update_json"),
    path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee_edit"),
    path("employees/<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="employee_delete"),

    path("objects/", views.object_list, name="object_list"),
    path("objects/create/", views.SiteObjectCreateView.as_view(), name="object_create"),
    path("objects/<int:pk>/detail/", views.object_detail_json, name="object_detail_json"),
    path("objects/<int:pk>/update/", views.object_update_json, name="object_update_json"),
    path("objects/<int:pk>/edit/", views.SiteObjectUpdateView.as_view(), name="object_edit"),
    path("objects/<int:pk>/delete/", views.SiteObjectDeleteView.as_view(), name="object_delete"),

    path("documents/", views.document_list, name="document_list"),
    path("documents/create/", views.DocumentCreateView.as_view(), name="document_create"),
    path("documents/<int:pk>/detail/", views.document_detail_json, name="document_detail_json"),
    path("documents/<int:pk>/update/", views.document_update_json, name="document_update_json"),
    path("documents/<int:pk>/attach/", views.document_attachment_create, name="document_attachment_create"),
    path("documents/<int:pk>/edit/", views.DocumentUpdateView.as_view(), name="document_edit"),
    path("documents/<int:pk>/delete/", views.DocumentDeleteView.as_view(), name="document_delete"),

    path("equipment/", views.equipment_list, name="equipment_list"),
    path("equipment/create/", views.EquipmentCreateView.as_view(), name="equipment_create"),
    path("equipment/<int:pk>/detail/", views.equipment_detail_json, name="equipment_detail_json"),
    path("equipment/<int:pk>/update/", views.equipment_update_json, name="equipment_update_json"),
    path("equipment/<int:pk>/upload-passport/", views.equipment_passport_upload, name="equipment_passport_upload"),
    path("equipment/<int:pk>/edit/", views.EquipmentUpdateView.as_view(), name="equipment_edit"),
    path("equipment/<int:pk>/delete/", views.EquipmentDeleteView.as_view(), name="equipment_delete"),

    path("registrations/", views.registration_list, name="registration_list"),
    path("registrations/create/", views.ObjectRegistrationCreateView.as_view(), name="registration_create"),
    path("registrations/<int:pk>/edit/", views.ObjectRegistrationUpdateView.as_view(), name="registration_edit"),
    path("registrations/<int:pk>/delete/", views.ObjectRegistrationDeleteView.as_view(), name="registration_delete"),

    path("objects/<int:pk>/document-create/", views.object_document_create, name="object_document_create"),
    path("objects/<int:pk>/document-quickupload/", views.object_document_quickupload, name="object_document_quickupload"),
    path("documents/<int:pk>/assign-object/", views.document_assign_object, name="document_assign_object"),

    path("object-equipment/", views.object_equipment_list, name="objectequipment_list"),
    path("object-equipment/create/", views.ObjectEquipmentCreateView.as_view(), name="objectequipment_create"),
    path("objects/<int:pk>/equipment-create-bind/", views.object_equipment_create_bind, name="object_equipment_create_bind"),
    path("object-equipment/bind/", views.object_equipment_bind, name="object_equipment_bind"),
    path("object-equipment/<int:pk>/unbind/", views.object_equipment_unbind, name="object_equipment_unbind"),
    path("object-equipment/<int:pk>/edit/", views.ObjectEquipmentUpdateView.as_view(), name="objectequipment_edit"),
    path("object-equipment/<int:pk>/delete/", views.ObjectEquipmentDeleteView.as_view(), name="objectequipment_delete"),
]