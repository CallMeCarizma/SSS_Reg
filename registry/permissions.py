from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

STAFF_GROUP = "Сотрудники"


def user_can_edit(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=STAFF_GROUP).exists()
    )


def user_can_delete(user):
    return user.is_authenticated and user.is_superuser


def edit_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not user_can_edit(request.user):
            raise PermissionDenied("Недостаточно прав для редактирования.")
        return view_func(request, *args, **kwargs)

    return wraps(view_func)(_wrapped)


def delete_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not user_can_delete(request.user):
            raise PermissionDenied("Недостаточно прав для удаления.")
        return view_func(request, *args, **kwargs)

    return wraps(view_func)(_wrapped)


class EditRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return user_can_edit(self.request.user)


class DeleteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return user_can_delete(self.request.user)
