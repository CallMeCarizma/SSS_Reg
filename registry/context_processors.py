from .permissions import user_can_delete, user_can_edit


def permissions(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"can_edit": False, "can_delete": False}
    return {
        "can_edit": user_can_edit(user),
        "can_delete": user_can_delete(user),
    }
