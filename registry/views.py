from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from .models import DocumentAttachment
from .permissions import edit_required, delete_required, EditRequiredMixin, DeleteRequiredMixin

from .forms import (
    ContractorForm,
    EmployeeForm,
    SiteObjectForm,
    DocumentForm,
    DocumentCreateForm,
    DocumentAttachmentForm,
    EquipmentForm,
    ObjectRegistrationForm,
    ObjectEquipmentForm,
)
from .models import (
    Contractor,
    Employee,
    SiteObject,
    Document,
    Equipment,
    ObjectRegistration,
    ObjectEquipment,
)


def _resolve_attr(obj, attr_path):
    value = obj
    for part in attr_path.split("."):
        if value is None:
            return None
        value = getattr(value, part, None)
        if callable(value):
            value = value()
    return value


def _build_rows(items, columns):
    rows = []
    for obj in items:
        values = {}
        for col in columns:
            values[col["name"]] = _resolve_attr(obj, col["source"])
        rows.append({
            "object": obj,
            "values": values,
        })
    return rows


@login_required
def dashboard(request):
    from datetime import date, timedelta
    today = date.today()

    stats = {
        "contractors": Contractor.objects.count(),
        "employees": Employee.objects.count(),
        "objects": SiteObject.objects.count(),
        "documents": Document.objects.count(),
        "equipment": Equipment.objects.count(),
    }

    latest_documents = Document.objects.select_related("object").order_by("-id")[:8]
    objects_with_docs = SiteObject.objects.annotate(doc_count=Count("documents")).order_by("-doc_count", "name")[:8]
    expiring_equipment = (
        Equipment.objects.filter(
            next_verification_date__isnull=False,
            next_verification_date__lte=today + timedelta(days=30),
        )
        .order_by("next_verification_date")[:15]
    )

    return render(request, "registry/dashboard.html", {
        "stats": stats,
        "latest_documents": latest_documents,
        "objects_with_docs": objects_with_docs,
        "expiring_equipment": expiring_equipment,
        "today": today,
    })

@delete_required
def document_attachment_delete(request, pk):
    attachment = get_object_or_404(DocumentAttachment, pk=pk)
    document_id = attachment.document_id

    if request.method == "POST":
        attachment.file.delete(save=False)
        attachment.delete()
        return redirect("document_edit", pk=document_id)

    return render(request, "registry/confirm_delete.html", {
        "title": "Удалить вложение",
        "object": attachment,
    })



def _contractor_json(c):
    return {
        'id': c.id,
        'name': c.name,
        'full_name': c.full_name,
        'type': c.type,
        'type_display': c.get_type_display(),
        'inn': c.inn,
        'kpp': c.kpp,
        'ogrn': c.ogrn,
        'address': c.address,
        'contact_person': c.contact_person,
        'phone': c.phone,
        'note': c.note,
    }


def _employee_json(e):
    return {
        'id': e.id,
        'full_name': e.full_name,
        'email': e.email,
        'phone': e.phone,
        'passport_data': e.passport_data,
    }


@login_required
def contractor_list(request):
    q = request.GET.get("q", "").strip()
    items = Contractor.objects.order_by("name")
    if q:
        items = items.filter(
            Q(name__icontains=q) | Q(inn__icontains=q) | Q(address__icontains=q)
        )
    type_choices = [{'value': k, 'label': v} for k, v in Contractor.TYPE_CHOICES]
    return render(request, "registry/contractor_list.html", {
        "title": "Контрагенты",
        "items": items,
        "q": q,
        "type_choices": type_choices,
    })


@login_required
def contractor_detail_json(request, pk):
    c = get_object_or_404(Contractor, pk=pk)
    return JsonResponse(_contractor_json(c))


@edit_required
def contractor_update_json(request, pk):
    import json
    c = get_object_or_404(Contractor, pk=pk)
    data = json.loads(request.body)
    form = ContractorForm(data, instance=c)
    if form.is_valid():
        c = form.save()
        return JsonResponse(_contractor_json(c))
    return JsonResponse({'errors': form.errors}, status=400)


@login_required
def employee_list(request):
    q = request.GET.get("q", "").strip()
    items = Employee.objects.order_by("full_name")
    if q:
        items = items.filter(
            Q(full_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q)
        )
    return render(request, "registry/employee_list.html", {
        "title": "Сотрудники",
        "items": items,
        "q": q,
    })


@login_required
def employee_detail_json(request, pk):
    e = get_object_or_404(Employee, pk=pk)
    return JsonResponse(_employee_json(e))


@edit_required
def employee_update_json(request, pk):
    import json
    e = get_object_or_404(Employee, pk=pk)
    data = json.loads(request.body)
    form = EmployeeForm(data, instance=e)
    if form.is_valid():
        e = form.save()
        return JsonResponse(_employee_json(e))
    return JsonResponse({'errors': form.errors}, status=400)


@login_required
def object_list(request):
    q = request.GET.get("q", "").strip()
    items = SiteObject.objects.all().order_by("name")

    if q:
        items = items.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(contractor__name__icontains=q) |
            Q(responsible__full_name__icontains=q)
        )

    all_equipment = [
        {'id': e.id, 'name': e.name, 'type_display': e.get_type_display()}
        for e in Equipment.objects.all().order_by('name')
    ]
    eq_type_choices = [{'value': k, 'label': v} for k, v in Equipment.TYPE_CHOICES]
    all_docs = [
        {
            'id': d.id,
            'title': str(d),
            'doc_type': d.doc_type,
            'object_id': d.object_id,
            'object_name': d.object.name if d.object else None,
        }
        for d in Document.objects.select_related('object').order_by('-id')
    ]
    doc_type_choices = [{'value': k, 'label': v} for k, v in Document.DOC_TYPE_CHOICES]

    all_contractors = [
        {'id': c.id, 'name': c.name}
        for c in Contractor.objects.order_by('name')
    ]
    all_employees = [
        {'id': e.id, 'name': e.full_name}
        for e in Employee.objects.order_by('full_name')
    ]

    from datetime import date as _date, timedelta
    _threshold = _date.today() + timedelta(days=30)
    objs_with_expiring_eq = set(
        ObjectEquipment.objects.filter(
            equipment__next_verification_date__isnull=False,
            equipment__next_verification_date__lte=_threshold,
        ).values_list('object_id', flat=True)
    )

    return render(request, "registry/object_list.html", {
        "title": "Объекты",
        "items": items,
        "q": q,
        "all_equipment": all_equipment,
        "eq_type_choices": eq_type_choices,
        "all_docs": all_docs,
        "doc_type_choices": doc_type_choices,
        "all_contractors": all_contractors,
        "all_employees": all_employees,
        "objs_with_expiring_eq": objs_with_expiring_eq,
    })


_STATUS_CLASSES = {
    'active': 'bg-success',
    'invalid': 'bg-warning text-dark',
    'delete': 'bg-danger',
}


def _warning_level(next_date):
    if not next_date:
        return None
    from datetime import date
    days = (next_date - date.today()).days
    if days <= 7:
        return 'red'
    if days <= 15:
        return 'orange'
    if days <= 30:
        return 'yellow'
    return None


def _doc_for_object_json(doc):
    return {
        'id': doc.id,
        'title': str(doc),
        'doc_type': doc.doc_type,
        'doc_type_display': doc.get_doc_type_display(),
        'doc_date_display': doc.doc_date.strftime('%d.%m.%Y') if doc.doc_date else '—',
        'attachment_count': len(doc.attachments.all()),
    }


def _site_object_json(obj):
    equipment = [
        {
            'link_id': oe.id,
            'equipment_id': oe.equipment_id,
            'name': oe.equipment.name,
            'type_display': oe.equipment.get_type_display(),
            'next_verification_date_display': (
                oe.equipment.next_verification_date.strftime('%d.%m.%Y')
                if oe.equipment.next_verification_date else '—'
            ),
            'verification_warning': _warning_level(oe.equipment.next_verification_date),
        }
        for oe in obj.objectequipment_set.select_related('equipment').all()
    ]
    documents = [_doc_for_object_json(doc) for doc in obj.documents.all()]
    return {
        'id': obj.id,
        'name': obj.name,
        'full_name': obj.full_name,
        'address': obj.address,
        'contractor_id': obj.contractor_id,
        'contractor_name': obj.contractor.name if obj.contractor else None,
        'responsible_id': obj.responsible_id,
        'responsible_name': obj.responsible.full_name if obj.responsible else None,
        'status': obj.status,
        'status_display': obj.get_status_display(),
        'status_class': _STATUS_CLASSES.get(obj.status, 'bg-secondary'),
        'is_opo': obj.is_opo,
        'equipment': equipment,
        'documents': documents,
    }


_OBJ_PREFETCH = ['objectequipment_set__equipment', 'documents__attachments']


@login_required
def object_detail_json(request, pk):
    obj = get_object_or_404(
        SiteObject.objects.select_related('contractor', 'responsible').prefetch_related(*_OBJ_PREFETCH),
        pk=pk,
    )
    return JsonResponse(_site_object_json(obj))


@edit_required
def object_update_json(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    obj = get_object_or_404(SiteObject, pk=pk)

    import json as _json
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = str(data.get('name', '')).strip()
    if not name:
        return JsonResponse({'errors': {'name': ['Наименование обязательно']}}, status=400)

    valid_statuses = [c[0] for c in SiteObject.STATUS_CHOICES]
    status = str(data.get('status', 'active'))

    def _fk_id(key):
        val = data.get(key)
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    obj.name = name
    obj.full_name = str(data.get('full_name', ''))
    obj.address = str(data.get('address', ''))
    obj.contractor_id = _fk_id('contractor_id')
    obj.responsible_id = _fk_id('responsible_id')
    obj.status = status if status in valid_statuses else 'active'
    obj.is_opo = bool(data.get('is_opo', False))
    obj.save()

    obj = SiteObject.objects.select_related('contractor', 'responsible').prefetch_related(*_OBJ_PREFETCH).get(pk=pk)
    return JsonResponse(_site_object_json(obj))


@edit_required
def object_document_create(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    obj = get_object_or_404(SiteObject, pk=pk)

    import json as _json
    from datetime import date as _date
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    title = str(data.get('title', '')).strip()
    if not title:
        return JsonResponse({'errors': {'title': ['Название обязательно']}}, status=400)

    valid_types = [c[0] for c in Document.DOC_TYPE_CHOICES]
    doc_type = str(data.get('doc_type', 'other'))
    if doc_type not in valid_types:
        doc_type = 'other'

    doc_date = None
    date_str = str(data.get('doc_date', ''))
    if date_str:
        try:
            doc_date = _date.fromisoformat(date_str)
        except ValueError:
            pass

    doc = Document.objects.create(
        object=obj,
        title=title,
        doc_type=doc_type,
        number=str(data.get('number', '')),
        doc_date=doc_date,
    )
    doc = Document.objects.prefetch_related('attachments').get(pk=doc.pk)
    return JsonResponse(_doc_for_object_json(doc))


@edit_required
def object_document_quickupload(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    obj = get_object_or_404(SiteObject, pk=pk)
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'Файл не указан'}, status=400)

    uploaded = request.FILES['file']
    filename = uploaded.name
    title = filename.rsplit('.', 1)[0] if '.' in filename else filename
    title = title.replace('_', ' ').replace('-', ' ')

    doc = Document.objects.create(object=obj, title=title, doc_type='other')
    DocumentAttachment.objects.create(document=doc, file=uploaded)
    doc = Document.objects.prefetch_related('attachments').get(pk=doc.pk)
    return JsonResponse(_doc_for_object_json(doc))


@edit_required
def document_assign_object(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    doc = get_object_or_404(Document, pk=pk)

    import json as _json
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        new_obj = SiteObject.objects.get(pk=int(data.get('object_id', 0)))
    except (SiteObject.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Объект не найден'}, status=404)

    doc.object = new_obj
    doc.save()
    return JsonResponse({'ok': True, 'doc_id': doc.id})


def _document_json(doc):
    return {
        'id': doc.id,
        'doc_type': doc.doc_type,
        'doc_type_display': doc.get_doc_type_display(),
        'title': doc.title,
        'number': doc.number,
        'doc_date': doc.doc_date.strftime('%Y-%m-%d') if doc.doc_date else '',
        'doc_date_display': doc.doc_date.strftime('%d.%m.%Y') if doc.doc_date else '—',
        'object_id': doc.object_id,
        'object_name': doc.object.name if doc.object else '—',
        'attachments': [
            {'id': a.id, 'name': str(a), 'url': a.file.url}
            for a in doc.attachments.all()
        ],
    }


@login_required
def document_detail_json(request, pk):
    doc = get_object_or_404(
        Document.objects.select_related('object').prefetch_related('attachments'), pk=pk
    )
    return JsonResponse(_document_json(doc))


@edit_required
def document_update_json(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    doc = get_object_or_404(Document, pk=pk)

    import json as _json
    from datetime import date as _date
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    title = str(data.get('title', '')).strip()
    if not title:
        return JsonResponse({'errors': {'title': ['Название обязательно']}}, status=400)

    valid_types = [c[0] for c in Document.DOC_TYPE_CHOICES]
    doc_type = str(data.get('doc_type', 'other'))
    doc.title = title
    doc.number = str(data.get('number', ''))
    doc.doc_type = doc_type if doc_type in valid_types else 'other'

    date_str = str(data.get('doc_date', ''))
    if date_str:
        try:
            doc.doc_date = _date.fromisoformat(date_str)
        except ValueError:
            doc.doc_date = None
    else:
        doc.doc_date = None

    obj_id = data.get('object_id')
    if obj_id:
        try:
            doc.object = SiteObject.objects.get(pk=int(obj_id))
        except (SiteObject.DoesNotExist, ValueError, TypeError):
            pass

    doc.save()
    doc = Document.objects.select_related('object').prefetch_related('attachments').get(pk=pk)
    return JsonResponse(_document_json(doc))


@edit_required
def document_attachment_create(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    doc = get_object_or_404(Document, pk=pk)
    form = DocumentAttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        att = form.save(commit=False)
        att.document = doc
        att.save()
        return JsonResponse({'id': att.id, 'name': str(att), 'url': att.file.url})
    return JsonResponse({'error': 'Неверный файл'}, status=400)


@login_required
def document_list(request):
    q = request.GET.get("q", "").strip()
    object_id = request.GET.get("object_id", "").strip()
    items = Document.objects.select_related("object").all().order_by("-id")

    if object_id and object_id.isdigit():
        items = items.filter(object_id=object_id)

    if q:
        items = items.filter(
            Q(title__icontains=q) |
            Q(doc_type__icontains=q) |
            Q(number__icontains=q) |
            Q(object__name__icontains=q)
        )

    filter_object = SiteObject.objects.filter(pk=object_id).first() if object_id and object_id.isdigit() else None
    title = f"Документы — {filter_object.name}" if filter_object else "Документы"

    all_objects = [{'id': o.id, 'name': o.name} for o in SiteObject.objects.all().order_by('name')]
    doc_type_choices = [{'value': k, 'label': v} for k, v in Document.DOC_TYPE_CHOICES]

    return render(request, "registry/document_list.html", {
        "title": title,
        "items": items,
        "q": q,
        "all_objects": all_objects,
        "doc_type_choices": doc_type_choices,
    })


def _equipment_json(eq):
    objects_list = [
        {'link_id': oe.id, 'object_id': oe.object_id, 'object_name': oe.object.name}
        for oe in eq.objectequipment_set.select_related('object').all()
    ]
    freq = eq.checking_frequency
    return {
        'id': eq.id,
        'type': eq.type,
        'type_display': eq.get_type_display(),
        'name': eq.name,
        'checking_frequency': freq,
        'checking_frequency_display': f'{freq} дн.' if freq else '—',
        'verification_date': eq.verification_date.strftime('%Y-%m-%d') if eq.verification_date else '',
        'verification_date_display': eq.verification_date.strftime('%d.%m.%Y') if eq.verification_date else '—',
        'next_verification_date': eq.next_verification_date.strftime('%Y-%m-%d') if eq.next_verification_date else '',
        'next_verification_date_display': eq.next_verification_date.strftime('%d.%m.%Y') if eq.next_verification_date else '—',
        'verification_warning': _warning_level(eq.next_verification_date),
        'passport_scan_url': eq.passport_scan.url if eq.passport_scan else '',
        'passport_scan_name': eq.passport_scan.name.split('/')[-1] if eq.passport_scan else '',
        'objects': objects_list,
    }


@login_required
def equipment_detail_json(request, pk):
    eq = get_object_or_404(
        Equipment.objects.prefetch_related('objectequipment_set__object'), pk=pk
    )
    return JsonResponse(_equipment_json(eq))


@edit_required
def equipment_update_json(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    eq = get_object_or_404(Equipment, pk=pk)

    import json as _json
    from datetime import date as _date
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = str(data.get('name', '')).strip()
    if not name:
        return JsonResponse({'errors': {'name': ['Наименование обязательно']}}, status=400)

    valid_types = [c[0] for c in Equipment.TYPE_CHOICES]
    eq_type = str(data.get('type', 'other'))
    eq.name = name
    eq.type = eq_type if eq_type in valid_types else 'other'

    try:
        eq.checking_frequency = int(data.get('checking_frequency')) if data.get('checking_frequency') not in (None, '') else None
    except (ValueError, TypeError):
        eq.checking_frequency = None

    date_str = str(data.get('verification_date', ''))
    if date_str:
        try:
            eq.verification_date = _date.fromisoformat(date_str)
        except ValueError:
            eq.verification_date = None
    else:
        eq.verification_date = None

    from datetime import timedelta
    if eq.verification_date and eq.checking_frequency:
        eq.next_verification_date = eq.verification_date + timedelta(days=eq.checking_frequency)
    else:
        eq.next_verification_date = None

    eq.save()
    eq = Equipment.objects.prefetch_related('objectequipment_set__object').get(pk=pk)
    return JsonResponse(_equipment_json(eq))


@edit_required
def equipment_passport_upload(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    eq = get_object_or_404(Equipment, pk=pk)
    if 'passport_scan' not in request.FILES:
        return JsonResponse({'error': 'Файл не указан'}, status=400)
    if eq.passport_scan:
        eq.passport_scan.delete(save=False)
    eq.passport_scan = request.FILES['passport_scan']
    eq.save()
    eq = Equipment.objects.prefetch_related('objectequipment_set__object').get(pk=pk)
    return JsonResponse(_equipment_json(eq))


@login_required
def equipment_list(request):
    q = request.GET.get("q", "").strip()
    object_id = request.GET.get("object_id", "").strip()
    items = Equipment.objects.all().order_by("name")

    if object_id and object_id.isdigit():
        items = items.filter(objectequipment__object_id=object_id)

    if q:
        items = items.filter(
            Q(type__icontains=q) |
            Q(name__icontains=q)
        )

    filter_object = SiteObject.objects.filter(pk=object_id).first() if object_id and object_id.isdigit() else None
    title = f"Оборудование — {filter_object.name}" if filter_object else "Оборудование"

    eq_type_choices = [{'value': k, 'label': v} for k, v in Equipment.TYPE_CHOICES]
    all_objects = [{'id': o.id, 'name': o.name} for o in SiteObject.objects.all().order_by('name')]

    return render(request, "registry/equipment_list.html", {
        "title": title,
        "items": items,
        "q": q,
        "eq_type_choices": eq_type_choices,
        "all_objects": all_objects,
    })


@login_required
def registration_list(request):
    q = request.GET.get("q", "").strip()

    items = ObjectRegistration.objects.select_related("object").all().order_by("-issued_at", "-id")

    if q:
        items = items.filter(
            Q(object__name__icontains=q) |
            Q(reg_number__icontains=q)
        )

    columns = [
        {"name": "id", "label": "ID", "source": "id"},
        {"name": "object", "label": "Объект", "source": "object.name"},
        {"name": "reg_number", "label": "Номер регистрации", "source": "reg_number"},
        {"name": "issued_at", "label": "Дата выдачи", "source": "issued_at", "type": "date"},
        {"name": "is_active", "label": "Статус", "source": "is_active", "type": "badge", "true_label": "Активна", "false_label": "Неактивна"},
    ]

    return render(request, "registry/list.html", {
        "title": "Регистрации",
        "items": items,
        "rows": _build_rows(items, columns),
        "q": q,
        "create_url": "registration_create",
        "edit_url": "registration_edit",
        "delete_url": "registration_delete",
        "columns": columns,
    })


@login_required
def object_equipment_list(request):
    q = request.GET.get("q", "").strip()
    object_id = request.GET.get("object_id", "").strip()
    items = ObjectEquipment.objects.select_related("object", "equipment").all().order_by("object__name", "equipment__name")

    if object_id and object_id.isdigit():
        items = items.filter(object_id=object_id)

    if q:
        items = items.filter(
            Q(object__name__icontains=q) |
            Q(equipment__name__icontains=q)
        )

    filter_object = SiteObject.objects.filter(pk=object_id).first() if object_id and object_id.isdigit() else None
    title = f"Оборудование — {filter_object.name}" if filter_object else "Оборудование на объектах"

    columns = [
        {"name": "id", "label": "ID", "source": "id"},
        {"name": "object", "label": "Объект", "source": "object.name"},
        {"name": "equipment", "label": "Оборудование", "source": "equipment.name"},
        {"name": "equipment_type", "label": "Тип", "source": "equipment.get_type_display"},
        {"name": "checking_frequency", "label": "Периодичность поверки", "source": "equipment.checking_frequency"},
        {"name": "verification_date", "label": "Дата поверки", "source": "equipment.verification_date", "type": "date"},
    ]

    return render(request, "registry/list.html", {
        "title": title,
        "items": items,
        "rows": _build_rows(items, columns),
        "q": q,
        "create_url": "objectequipment_create",
        "edit_url": "objectequipment_edit",
        "delete_url": "objectequipment_delete",
        "columns": columns,
    })


@edit_required
def object_equipment_create_bind(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    obj = get_object_or_404(SiteObject, pk=pk)

    import json as _json
    from datetime import date as _date, timedelta
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = str(data.get('name', '')).strip()
    if not name:
        return JsonResponse({'errors': {'name': ['Наименование обязательно']}}, status=400)

    valid_types = [c[0] for c in Equipment.TYPE_CHOICES]
    eq_type = str(data.get('type', 'other'))
    if eq_type not in valid_types:
        eq_type = 'other'

    try:
        freq = int(data.get('checking_frequency')) if data.get('checking_frequency') not in (None, '') else None
    except (ValueError, TypeError):
        freq = None

    verification_date = None
    date_str = str(data.get('verification_date', ''))
    if date_str:
        try:
            verification_date = _date.fromisoformat(date_str)
        except ValueError:
            pass

    next_verification_date = None
    if verification_date and freq:
        next_verification_date = verification_date + timedelta(days=freq)

    eq = Equipment.objects.create(
        name=name,
        type=eq_type,
        checking_frequency=freq,
        verification_date=verification_date,
        next_verification_date=next_verification_date,
    )
    ObjectEquipment.objects.create(object=obj, equipment=eq)
    return JsonResponse({'ok': True, 'equipment_id': eq.id})


@edit_required
def object_equipment_bind(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    import json as _json
    try:
        data = _json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    try:
        obj = SiteObject.objects.get(pk=int(data.get('object_id', 0)))
        eq = Equipment.objects.get(pk=int(data.get('equipment_id', 0)))
    except (SiteObject.DoesNotExist, Equipment.DoesNotExist, (ValueError, TypeError)):
        return JsonResponse({'error': 'Объект или оборудование не найдено'}, status=404)
    oe, _ = ObjectEquipment.objects.get_or_create(object=obj, equipment=eq)
    return JsonResponse({'ok': True, 'link_id': oe.id})


@delete_required
def object_equipment_unbind(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    oe = get_object_or_404(ObjectEquipment, pk=pk)
    oe.delete()
    return JsonResponse({'ok': True})


class BaseRegistryCreateView(EditRequiredMixin, CreateView):
    template_name = "registry/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        return context


class BaseRegistryUpdateView(EditRequiredMixin, UpdateView):
    template_name = "registry/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        return context


class BaseRegistryDeleteView(DeleteRequiredMixin, DeleteView):
    template_name = "registry/confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        return context


class ContractorCreateView(BaseRegistryCreateView):
    model = Contractor
    form_class = ContractorForm
    success_url = reverse_lazy("contractor_list")
    page_title = "Добавить контрагента"


class ContractorUpdateView(BaseRegistryUpdateView):
    model = Contractor
    form_class = ContractorForm
    success_url = reverse_lazy("contractor_list")
    page_title = "Изменить контрагента"


class ContractorDeleteView(BaseRegistryDeleteView):
    model = Contractor
    success_url = reverse_lazy("contractor_list")
    page_title = "Удалить контрагента"


class EmployeeCreateView(BaseRegistryCreateView):
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy("employee_list")
    page_title = "Добавить сотрудника"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f'Сотрудник «{self.object.full_name}» добавлен.')
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(str(self.success_url))


class EmployeeUpdateView(BaseRegistryUpdateView):
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy("employee_list")
    page_title = "Изменить сотрудника"


class EmployeeDeleteView(BaseRegistryDeleteView):
    model = Employee
    success_url = reverse_lazy("employee_list")
    page_title = "Удалить сотрудника"


class SiteObjectCreateView(BaseRegistryCreateView):
    model = SiteObject
    form_class = SiteObjectForm
    success_url = reverse_lazy("object_list")
    page_title = "Добавить объект"


class SiteObjectUpdateView(BaseRegistryUpdateView):
    model = SiteObject
    form_class = SiteObjectForm
    success_url = reverse_lazy("object_list")
    page_title = "Изменить объект"


class SiteObjectDeleteView(BaseRegistryDeleteView):
    model = SiteObject
    success_url = reverse_lazy("object_list")
    page_title = "Удалить объект"


class DocumentCreateView(BaseRegistryCreateView):
    model = Document
    form_class = DocumentCreateForm
    success_url = reverse_lazy("document_list")
    page_title = "Добавить документ"

    def get_initial(self):
        initial = super().get_initial()
        obj_id = self.request.GET.get('object_id', '').strip()
        if obj_id.isdigit():
            try:
                initial['object'] = SiteObject.objects.get(pk=int(obj_id))
            except SiteObject.DoesNotExist:
                pass
        return initial

    def get_success_url(self):
        obj_id = self.request.GET.get('object_id', '').strip()
        if obj_id.isdigit():
            return f'/objects/?select={obj_id}'
        return str(self.success_url)

    def form_valid(self, form):
        self.object = form.save()
        for f in self.request.FILES.getlist('attachment'):
            DocumentAttachment.objects.create(document=self.object, file=f)
        messages.success(self.request, f'Документ «{self.object.title}» создан.')
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())



class DocumentDeleteView(BaseRegistryDeleteView):
    model = Document
    success_url = reverse_lazy("document_list")
    page_title = "Удалить документ"


class EquipmentCreateView(BaseRegistryCreateView):
    model = Equipment
    form_class = EquipmentForm
    success_url = reverse_lazy("equipment_list")
    page_title = "Добавить оборудование"

    def get_initial(self):
        initial = super().get_initial()
        obj_id = self.request.GET.get('object_id', '').strip()
        if obj_id.isdigit():
            try:
                initial['bind_object'] = SiteObject.objects.get(pk=int(obj_id))
            except SiteObject.DoesNotExist:
                pass
        return initial

    def get_success_url(self):
        obj_id = self.request.GET.get('object_id', '').strip()
        if obj_id.isdigit():
            return f'/objects/?select={obj_id}'
        return str(self.success_url)

    def form_valid(self, form):
        from datetime import timedelta
        self.object = form.save(commit=False)
        if self.object.verification_date and self.object.checking_frequency:
            self.object.next_verification_date = self.object.verification_date + timedelta(days=self.object.checking_frequency)
        self.object.save()
        bind_object = form.cleaned_data.get('bind_object')
        if bind_object:
            ObjectEquipment.objects.get_or_create(object=bind_object, equipment=self.object)
        messages.success(self.request, f'Оборудование «{self.object.name}» создано.')
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())


class EquipmentUpdateView(BaseRegistryUpdateView):
    model = Equipment
    form_class = EquipmentForm
    success_url = reverse_lazy("equipment_list")
    page_title = "Изменить оборудование"


class EquipmentDeleteView(BaseRegistryDeleteView):
    model = Equipment
    success_url = reverse_lazy("equipment_list")
    page_title = "Удалить оборудование"


class ObjectRegistrationCreateView(BaseRegistryCreateView):
    model = ObjectRegistration
    form_class = ObjectRegistrationForm
    success_url = reverse_lazy("registration_list")
    page_title = "Добавить регистрацию"


class ObjectRegistrationUpdateView(BaseRegistryUpdateView):
    model = ObjectRegistration
    form_class = ObjectRegistrationForm
    success_url = reverse_lazy("registration_list")
    page_title = "Изменить регистрацию"


class ObjectRegistrationDeleteView(BaseRegistryDeleteView):
    model = ObjectRegistration
    success_url = reverse_lazy("registration_list")
    page_title = "Удалить регистрацию"


class ObjectEquipmentCreateView(BaseRegistryCreateView):
    model = ObjectEquipment
    form_class = ObjectEquipmentForm
    success_url = reverse_lazy("objectequipment_list")
    page_title = "Добавить оборудование на объект"


class ObjectEquipmentUpdateView(BaseRegistryUpdateView):
    model = ObjectEquipment
    form_class = ObjectEquipmentForm
    success_url = reverse_lazy("objectequipment_list")
    page_title = "Изменить оборудование на объекте"


class ObjectEquipmentDeleteView(BaseRegistryDeleteView):
    model = ObjectEquipment
    success_url = reverse_lazy("objectequipment_list")
    page_title = "Удалить оборудование с объекта"

class DocumentUpdateView(BaseRegistryUpdateView):
    model = Document
    form_class = DocumentForm
    success_url = reverse_lazy("document_list")
    page_title = "Изменить документ"
    template_name = "registry/document_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachment_form"] = kwargs.get("attachment_form", DocumentAttachmentForm())
        context["attachments"] = self.object.attachments.all().order_by("-id")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if "upload_attachment" in request.POST:
            attachment_form = DocumentAttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.document = self.object
                attachment.save()
                return redirect("document_edit", pk=self.object.pk)

            context = self.get_context_data(
                form=self.get_form(),
                attachment_form=attachment_form,
            )
            return self.render_to_response(context)


@login_required
def global_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    results = []
    for obj in SiteObject.objects.filter(Q(name__icontains=q) | Q(full_name__icontains=q)).order_by('name')[:6]:
        results.append({'icon': 'bi-buildings', 'type_label': 'Объект', 'title': obj.name,
                        'sub': obj.get_status_display(), 'url': f'/objects/?select={obj.id}'})
    for c in Contractor.objects.filter(Q(name__icontains=q) | Q(inn__icontains=q)).order_by('name')[:6]:
        results.append({'icon': 'bi-people', 'type_label': 'Контрагент', 'title': c.name,
                        'sub': c.get_type_display(), 'url': f'/contractors/?select={c.id}'})
    for e in Employee.objects.filter(Q(full_name__icontains=q) | Q(email__icontains=q)).order_by('full_name')[:6]:
        results.append({'icon': 'bi-person-badge', 'type_label': 'Сотрудник', 'title': e.full_name,
                        'sub': e.email or e.phone or '', 'url': f'/employees/?select={e.id}'})
    for d in Document.objects.filter(Q(title__icontains=q) | Q(number__icontains=q)).order_by('-id')[:6]:
        results.append({'icon': 'bi-file-earmark-text', 'type_label': 'Документ', 'title': str(d),
                        'sub': d.get_doc_type_display(), 'url': f'/documents/?select={d.id}'})
    for eq in Equipment.objects.filter(name__icontains=q).order_by('name')[:6]:
        results.append({'icon': 'bi-tools', 'type_label': 'Оборудование', 'title': eq.name,
                        'sub': eq.get_type_display(), 'url': f'/equipment/?select={eq.id}'})
    return JsonResponse({'results': results})


@login_required
def equipment_calendar(request):
    import json as _json
    from datetime import date
    qs = Equipment.objects.filter(next_verification_date__isnull=False).order_by('next_verification_date')
    events = [
        {
            'id': eq.id, 'title': eq.name, 'type': eq.get_type_display(),
            'date': eq.next_verification_date.strftime('%Y-%m-%d'),
            'warning': eq.verification_warning,
            'url': f'/equipment/?select={eq.id}',
        }
        for eq in qs
    ]
    return render(request, 'registry/equipment_calendar.html', {
        'title': 'Календарь поверок',
        'events_json': _json.dumps(events, ensure_ascii=False),
        'today': date.today().strftime('%Y-%m-%d'),
    })