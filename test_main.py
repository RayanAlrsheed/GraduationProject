import datetime

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
cookies = {}


def test_invalid_register_email():
    response = client.post("/api/register", data={
        "email": "test",
        "password": "11111111",
        "password2": "11111111",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })
    assert response.status_code == 400


def test_invalid_register_email_match():
    response = client.post("/api/register", data={
        "email": "test@test.com",
        "password": "11111111",
        "password2": "11111111",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })
    assert response.status_code == 400

def test_invalid_register_password():
    response = client.post("/api/register", data={
        "email": "test_unit@test.com",
        "password": "1",
        "password2": "1",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })
    assert response.status_code == 400

def test_invalid_register_password_match():
    response = client.post("/api/register", data={
        "email": "test_unit@test.com",
        "password": "11111111",
        "password2": "11111112",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })
    assert response.status_code == 400

def test_invalid_register_phone():
    response = client.post("/api/register", data={
        "email": "test_unit@test.com",
        "password": "11111111",
        "password2": "11111111",
        "first_name": "test",
        "last_name": "test",
        "phone": "1234567890",
        "location": "Riyadh",
        "test": True
    })
    assert response.status_code == 400


def test_valid_register():
    response = client.post("/api/register", data={
        "email": "test_unit@test.com",
        "password": "11111111",
        "password2": "11111111",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })
    assert response.status_code == 200



def test_invalid_login_email():
    response = client.post("/api/login", data={
        "email": "test",
        "password": "12341234",
        "test": True
    })
    assert response.status_code == 400


def test_invalid_login_password():
    response = client.post("/api/login", data={
        "email": "test_unit@test.com",
        "password": "12345",
        "test": True
    })
    assert response.status_code == 401


def test_valid_login():

    response = client.post("/api/login", data={
        "email": "test_unit@test.com",
        "password": "11111111",
        "test": True
    })
    assert response.status_code == 200
    cookies["access_token_cookie"] = response.json()["access_token"]


def test_invalid_element_addition_id():

    response = client.post("/api/add_element", cookies=cookies, data={
        "name": "test",
        "test": True
    })

    assert response.status_code == 400


def test_invalid_element_addition_name():
    response = client.post("/api/add_element", cookies=cookies, data={
        "element_id": "test",
        "test": True
    })

    assert response.status_code == 400


def test_valid_element_addition():
    response = client.post("/api/add_element", cookies=cookies, data={
        "element_id": "test",
        "name": "test",
        "test": True
    })

    assert response.status_code == 200


def test_invalid_element_addition_exist():
    response = client.post("/api/add_element", cookies=cookies, data={
        "element_id": "test",
        "name": "test",
        "test": True
    })

    assert response.status_code == 400


def test_invalid_element_modification_exist():
    response = client.post("/api/add_element", cookies=cookies, data={
        "element_id_before": "test1",
        "element_id": "test",
        "name": "test",
        "test": True
    })

    assert response.status_code == 400


def test_invalid_element_modification_name():
    response = client.post("/api/edit_element", cookies=cookies, data={
        "element_id_before": "test",
        "element_id": "test1",
        "test": True
    })

    assert response.status_code == 400


def test_valid_element_modification():
    response = client.post("/api/edit_element", cookies=cookies, data={
        "element_id_before": "test",
        "element_id": "test1",
        "name": "test",
        "test": True
    })

    assert response.status_code == 200

    response = client.post("/api/edit_element", cookies=cookies, data={
        "element_id_before": "test1",
        "element_id": "test",
        "name": "test",
        "test": True
    })

    assert response.status_code == 200

def test_invalid_ingredient_addition_unit():
    response = client.post("/api/add_ingredient", cookies=cookies, data={
        "element_id": "test",
        "name": "test",
        "quantity": 100,
        "test": True
    })

    assert response.status_code == 400


def test_valid_ingredient_addition():
    response = client.post("/api/add_ingredient", cookies=cookies, data={
        "element_id": "test",
        "name": "test",
        "quantity": 100,
        "unit":"test",
        "test": True
    })

    assert response.status_code == 200

def test_invalid_ingredient_modification_number():
    response = client.post("/api/edit_ingredient", cookies=cookies, data={
        "element_id": "test",
        "name": "test",
        "quantity": 100,
        "unit": "test",
        "number": 1,
        "test": True
    })

    assert response.status_code == 400


def test_valid_ingredient_modification():
    response = client.post("/api/edit_ingredient", cookies=cookies, data={
        "element_id": "test",
        "name": "test",
        "quantity": 100,
        "unit": "test",
        "number": 0,
        "test": True
    })

    assert response.status_code == 200


def test_invalid_ingredient_deletion_id():
    response = client.post("/api/remove_ingredient", cookies=cookies, data={
        "element_id": "test1",
        "number": 0,
        "test": True
    })

    assert response.status_code == 400


def test_invalid_ingredient_deletion_number():
    response = client.post("/api/remove_ingredient", cookies=cookies, data={
        "element_id": "test",
        "number": 1,
        "test": True
    })

    assert response.status_code == 400


def test_valid_ingredient_deletion():
    response = client.post("/api/remove_ingredient", cookies=cookies, data={
        "element_id": "test",
        "number": 0,
        "test": True
    })

    assert response.status_code == 200


def test_invalid_element_deletion_exist():
    response = client.post("/api/remove_element", cookies=cookies, data={
        "element_id": "test1",
        "test": True
    })

    assert response.status_code == 400


def test_valid_element_deletion():
    response = client.post("/api/remove_element", cookies=cookies, data={
        "element_id": "test",
        "test": True
    })

    assert response.status_code == 200


def test_invalid_sale_addition_date():
    response = client.post("/api/add_sale", cookies=cookies, data={
        "element_id": "test",
        "quantity": 10,
        "test": True
    })

    assert response.status_code == 400


def test_invalid_sale_addition_id():
    response = client.post("/api/add_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "quantity": 10,
        "test": True
    })

    assert response.status_code == 400


def test_invalid_sale_addition_quantity():
    response = client.post("/api/add_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "element_id": "test",
        "test": True
    })

    assert response.status_code == 400


def test_valid_sale_addition():
    response = client.post("/api/add_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "element_id": "test",
        "quantity": 10,
        "test": True
    })

    assert response.status_code == 200


def test_invalid_sale_modification_missing():
    response = client.post("/api/edit_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "element_id": "test1",
        "quantity": 10,
        "test": True
    })

    assert response.status_code == 400


def test_invalid_sale_modification_time():
    response = client.post("/api/edit_sale", cookies=cookies, data={
        "element_id": "test",
        "quantity": 10,
        "test": True
    })

    assert response.status_code == 400



def test_valid_sale_modification():
    response = client.post("/api/edit_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "element_id": "test",
        "quantity": 5,
        "test": True
    })

    assert response.status_code == 200


def test_invalid_sale_deletion_missing():
    response = client.post("/api/remove_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "element_id": "test1",
        "test": True
    })

    assert response.status_code == 400


def test_valid_sale_deletion():
    response = client.post("/api/remove_sale", cookies=cookies, data={
        "time": datetime.date.today(),
        "element_id": "test",
        "test": True
    })

    assert response.status_code == 200


def test_invalid_settings_modification_password_match():
    response = client.post("/api/update_settings", data={
        "email": "test_unit@test.com",
        "password": "11111112",
        "password2": "11111111",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })

    assert response.status_code == 400


def test_invalid_settings_modification_email_exist():
    response = client.post("/api/update_settings", data={
        "email": "test@test.com",
        "password": "11111111",
        "password2": "11111111",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    })

    assert response.status_code == 400



def test_valid_settings_modification():
    response = client.post("/api/update_settings", data={
        "email": "test_unit@test.com",
        "password": "11111112",
        "password2": "11111112",
        "first_name": "test",
        "last_name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "test": True
    }, cookies=cookies)

    assert response.status_code == 200


def test_invalid_upload_file():
    with open("invalid_test.csv", "rb") as file:
        response = client.post("/api/upload", data={"test": True}, files={"file":file} ,cookies=cookies)

    assert response.status_code == 400


def test_valid_upload():
    with open("valid_test.csv", "rb") as file:
        response = client.post("/api/upload", data={"test": True}, files={"file":file}, cookies=cookies)

    assert response.status_code == 200


def test_invalid_charity_addition_permission():
    response = client.post("/api/add_charity", data={
        "name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "url": "www.google.com",
        "test": True
    })

    assert response.status_code == 401


def test_invalid_charity_modification_permission():
    response = client.post("/api/edit_charity", data={
        "name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "url": "www.google.com",
        "test": True
    })

    assert response.status_code == 401


def test_invalid_charity_deletion_permission():
    response = client.post("/api/remove_charity", data={
        "name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "url": "www.google.com",
        "test": True
    })

    assert response.status_code == 401


def test_delete_account():
    response = client.post("/api/delete", data={"test": True}, cookies=cookies)
    assert response.status_code == 200


def test_admin_login():
    response = client.post("/api/login", data={
        "email": "admin@admin.com",
        "password": "11111111",
        "test": True
    })
    assert response.status_code == 200
    cookies["access_token_cookie"] = response.json()["access_token"]


charity_id = ""


def test_invalid_charity_addition_name():
    global charity_id
    response = client.post("/api/add_charity", data={
        "phone": "0512345678",
        "location": "Riyadh",
        "url": "www.google.com",
        "test": True
    },cookies=cookies)
    assert response.status_code == 400


def test_valid_charity_addition():
    global charity_id
    response = client.post("/api/add_charity", data={
        "name": "test",
        "phone": "0512345678",
        "location": "Riyadh",
        "url": "www.google.com",
        "test": True
    }, cookies=cookies)
    assert response.status_code == 200
    charity_id = response.json()["id"]


def test_invalid_charity_modification_id():
    global charity_id
    response = client.post("/api/edit_charity", data={
        "id": "test",
        "name": "test",
        "location": "Riyadh",
        "url": "www.google.com",
        "test": True
    },cookies=cookies)

    assert response.status_code == 400


def test_valid_charity_modification():
    global charity_id
    response = client.post("/api/edit_charity", data={
        "id": charity_id,
        "name": "test",
        "phone": "0512345678",
        "location": "Jeddah",
        "url": "www.google.com",
        "test": True
    }, cookies=cookies)

    assert response.status_code == 200


def test_invalid_charity_deletion_id():
    global charity_id
    response = client.post("/api/remove_charity", data={
        "id": "test",
        "test": True
    },cookies=cookies)

    assert response.status_code == 400


def test_valid_charity_deletion():
    global charity_id
    response = client.post("/api/remove_charity", data={
        "id": charity_id,
        "test": True
    },cookies=cookies)

    assert response.status_code == 200

