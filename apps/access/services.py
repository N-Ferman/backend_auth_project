from apps.access.models import AccessRoleRule


def get_rules_for_user_and_element(user, element_code: str):
    return AccessRoleRule.objects.filter(
        role__user_roles__user=user,
        element__code=element_code,
    ).select_related("role", "element")


def get_read_scope(user, element_code: str) -> str:
    rules = get_rules_for_user_and_element(user, element_code)

    if rules.filter(read_all_permission=True).exists():
        return "all"

    if rules.filter(read_permission=True).exists():
        return "own"

    return "none"


def can_create(user, element_code: str) -> bool:
    return get_rules_for_user_and_element(
        user,
        element_code,
    ).filter(
        create_permission=True,
    ).exists()


def can_read_object(user, element_code: str, owner_id: int) -> bool:
    rules = get_rules_for_user_and_element(user, element_code)

    if rules.filter(read_all_permission=True).exists():
        return True

    if int(owner_id) == int(user.id) and rules.filter(read_permission=True).exists():
        return True

    return False


def can_update(user, element_code: str, owner_id: int) -> bool:
    rules = get_rules_for_user_and_element(user, element_code)

    if rules.filter(update_all_permission=True).exists():
        return True

    if int(owner_id) == int(user.id) and rules.filter(update_permission=True).exists():
        return True

    return False


def can_delete(user, element_code: str, owner_id: int) -> bool:
    rules = get_rules_for_user_and_element(user, element_code)

    if rules.filter(delete_all_permission=True).exists():
        return True

    if int(owner_id) == int(user.id) and rules.filter(delete_permission=True).exists():
        return True

    return False