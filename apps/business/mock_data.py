from apps.accounts.models import User


def get_other_user_id(current_user):
    other_user = (
        User.objects
        .filter(is_active=True)
        .exclude(id=current_user.id)
        .first()
    )

    if other_user:
        return other_user.id

    return current_user.id + 1000


def build_mock_objects(element_code: str, current_user):
    other_user_id = get_other_user_id(current_user)

    data = {
        "products": [
            {
                "id": 1,
                "title": "Laptop",
                "price": 1500,
                "owner_id": current_user.id,
            },
            {
                "id": 2,
                "title": "Phone",
                "price": 900,
                "owner_id": other_user_id,
            },
            {
                "id": 3,
                "title": "Headphones",
                "price": 200,
                "owner_id": other_user_id,
            },
        ],
        "orders": [
            {
                "id": 1,
                "title": "Order #1",
                "status": "created",
                "owner_id": current_user.id,
            },
            {
                "id": 2,
                "title": "Order #2",
                "status": "paid",
                "owner_id": other_user_id,
            },
            {
                "id": 3,
                "title": "Order #3",
                "status": "cancelled",
                "owner_id": current_user.id,
            },
        ],
        "stores": [
            {
                "id": 1,
                "title": "Main Store",
                "city": "Moscow",
                "owner_id": other_user_id,
            },
            {
                "id": 2,
                "title": "Small Store",
                "city": "Saint Petersburg",
                "owner_id": current_user.id,
            },
        ],
    }

    return data.get(element_code, [])


def find_mock_object(element_code: str, object_id: int, current_user):
    objects = build_mock_objects(element_code, current_user)

    for obj in objects:
        if int(obj["id"]) == int(object_id):
            return obj

    return None