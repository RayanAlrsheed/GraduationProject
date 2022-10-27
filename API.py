import codecs
import csv
from io import StringIO
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
import starlette.status as status
from passlib.context import CryptContext
import zipfile
import models
import re
from auth import AuthHandler
from mongoengine.queryset.visitor import Q
from datetime import datetime
from fastapi.responses import RedirectResponse
from schemas import RegistrationDetails, LoginDetails
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from bson import ObjectId
from datetime import date
from typing import Optional
templates = Jinja2Templates(directory="html")
router = APIRouter(prefix="/api")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@AuthJWT.load_config
def get_config():
    return Settings()


@router.post("/register")
def register(first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    password2: str = Form(None),
    phone: str = Form(None),
    location: str = Form(None),
    authorize: AuthJWT = Depends()):

    if not (first_name and last_name and email and password and password2 and phone and location):
        return RedirectResponse("/register?error=empty", status_code=302)

    if password != password2:
        return RedirectResponse("/register?error=match", status_code=302)

    if models.User.objects(Q(email=email)):
        return RedirectResponse("/register?error=email", status_code=302)
    if not re.fullmatch("0?5\d{8}", phone):
        return RedirectResponse("/register?error=phone", status_code=302)
    if not re.fullmatch("[A-Za-z0-9@#$%^&+=]{8,16}", password):
        return RedirectResponse("/register?error=password", status_code=302)

    user = models.User(first_name=first_name, last_name=last_name,email=email,
                       password=get_password_hash(password),
                       phone=phone, type="restaurant", created_at=datetime.utcnow())
    user.save()

    restaurant = models.Restaurant(user_id=user.id, location=location, menu=[])
    restaurant.save()

    orders = models.Orders(user_id=user.id)
    orders.save()

    access_token = authorize.create_access_token(subject=str(user.id))

    response = RedirectResponse("/", status_code=302)
    authorize.set_access_cookies(access_token, response=response)
    return response


@router.post("/login")
def login(email: str = Form(None), password : str = Form(None), authorize: AuthJWT = Depends()):
    print(email, password)
    if not email or not password:
        pass

    user = models.User.objects(Q(email=email))
    if not user:
        return RedirectResponse("../login?error=email", status_code=302)
    user = user[0]

    if not verify_password(password, user.password):
        return RedirectResponse("../login?error=password", status_code=302)

    access_token = authorize.create_access_token(subject=str(user.id))

    response = RedirectResponse("/", status_code=302)
    authorize.set_access_cookies(access_token, response=response)

    return response


@router.get("/logout")
def logout(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    response = RedirectResponse("/login", status_code=302)
    authorize.unset_jwt_cookies(response)

    return response

@router.post("/add_element")
def add_element(element_id: str = Form(None), name: str = Form(None), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    print(1)
    user_id = ObjectId(authorize.get_jwt_subject())
    restaurant = models.Restaurant.objects.get(user_id=user_id)

    if not (element_id and name):
        return RedirectResponse("/dashboard/menu")
    print(element_id, name)
    print(restaurant.add_element(element_id, name))

    return RedirectResponse("../menu", status_code=302)


@router.post("/edit_element")
def edit_element(element_id_before: str = Form(...) ,element_id: str = Form(...), name: str = Form(...),
                authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    restaurant = models.Restaurant.objects.get(user_id=user_id)

    if not (element_id or name):
        return RedirectResponse("../menu", status_code=302)

    restaurant.modify_element(element_id_before, element_id, name)

    return RedirectResponse(f"../menu/edit?element_id={element_id}", status_code=302)


@router.post("/remove_element")
def remove_element(element_id: str = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    restaurant = models.Restaurant.objects.get(user_id=user_id)

    if not element_id:
        pass

    restaurant.remove_element(element_id)

    return RedirectResponse(f"../menu", status_code=302)

@router.post("/add_ingredient")
def add_ingredient(element_id: str = Form(...), name: str = Form(...), quantity= Form(...), unit: str = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    restaurant = models.Restaurant.objects.get(user_id=user_id)

    if not (quantity and name and unit):
        return RedirectResponse("/dashboard/menu")

    if quantity:
        try:
            quantity = float(quantity)
        except:
            RedirectResponse(f"../menu/edit?element_id={element_id}")

    restaurant.add_ingredient(element_id, name, quantity, unit)

    return RedirectResponse(f"../menu/edit?element_id={element_id}", status_code=302)


@router.post("/edit_ingredient")
def edit_ingredient(element_id: str = Form(...), number: int = Form(...),
                   name: str = Form(...), quantity = Form(...), unit: str = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    restaurant = models.Restaurant.objects.get(user_id=user_id)

    if quantity:
        try:
            quantity = float(quantity)
        except:
            RedirectResponse(f"../edit_ingredient?element_id={element_id}&number={number}", status_code=302)

    if not (quantity and name and unit):
        return RedirectResponse("/menu")

    restaurant.modify_ingredient(element_id, number, name, quantity, unit)

    return RedirectResponse(f"/menu/edit?element_id={element_id}", status_code=302)


@router.post("/remove_ingredient")
def remove_ingredient(element_id: str = Form(...), number: int = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    restaurant = models.Restaurant.objects.get(user_id=user_id)

    if not element_id:
        pass

    restaurant.remove_ingredient(element_id, number)

    return RedirectResponse(f"../menu/edit?element_id={element_id}", status_code=302)



@router.post("/add_charity")
def add_charity(name: str = Form(...), phone: str = Form(...), location: str = Form(...),
                url: str = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    user = models.User.objects.get(id=user_id)
    if not user.is_admin():
        return RedirectResponse("/", status_code=302)

    if not (name or phone or location or url):
        return RedirectResponse("/", status_code=302)

    charity = models.Charity(name=name, phone=phone, location=location, location_url=url)

    charity.save()

    return RedirectResponse("/", status_code=302)


@router.post("/edit_charity")
def edit_charity(id:str = Form(...), name: str = Form(...), phone: str = Form(...), location: str = Form(...),
                url: str = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    user = models.User.objects.get(id=user_id)
    if not user.is_admin():
        return RedirectResponse("../charity")

    if not (name and phone and location and url and id):
        return RedirectResponse("/")
    try:
        charity = models.Charity.objects.get(id=ObjectId(id))

        charity.name = name
        charity.phone = phone
        charity.location = location
        charity.location_url = url
        charity.save()
    except:
        pass

    return RedirectResponse("/", status_code=302)


@router.post("/remove_charity")
def remove_charity(id:str = Form(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    user = models.User.objects.get(id=user_id)
    if not user.is_admin():
        return RedirectResponse("../charity")

    if not id:
        return RedirectResponse("../")

    try:
        charity = models.Charity.objects(id=ObjectId(id))

        charity.delete()
    except:
        pass

    return RedirectResponse("/", status_code=302)

@router.post("/add_sale")
def add_sale(time: date = Form(None), element_id: str = Form(None), quantity= Form(None), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    if quantity:
        try:
            quantity = float(quantity)
        except:
            RedirectResponse(f"../sales?time={time}", status_code=302)

    orders = models.Orders.objects.get(user_id=user_id)
    orders.add_sale_to_order(time, element_id, quantity)

    return RedirectResponse(f"../sales?time={time}", status_code=302)

@router.post("/edit_sale")
def edit_sale(time: date = Form(None), element_id: str = Form(None), quantity = Form(None), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    if quantity:
        try:
            quantity = float(quantity)
        except:
            RedirectResponse(f"../edit_sale?time={time}&element_id={element_id}", status_code=302)

    user_id = ObjectId(authorize.get_jwt_subject())
    orders = models.Orders.objects.get(user_id=user_id)
    order = orders.get_order(time)
    order.modify_sale(element_id, quantity)
    orders.save()

    return RedirectResponse(f"../sales?time={time}", status_code=302)

@router.post("/remove_sale")
def remove_sale(time: date = Form(None), element_id: str = Form(None), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    orders = models.Orders.objects.get(user_id=user_id)
    orders.remove_sale_from_order(time, element_id)

    return RedirectResponse(f"../sales?time={time}", status_code=302)

@router.post("/update_settings")
def update_settings(first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    password2: str = Form(None),
    phone: str = Form(None),
    location: str = Form(None),
    authorize: AuthJWT = Depends()):

    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()

    try:
        user = models.User.objects.get(id=user_id)
        restaurant = models.Restaurant.objects.get(user_id=ObjectId(user_id))
    except Exception as e:
        print(e)
        return RedirectResponse("../", status_code=302)

    if not (first_name and last_name and email and phone and location and phone and (not ((password and not password2) or (not password and password2)))):
        return RedirectResponse("../settings?error=empty", status_code=302)

    if password and password2 and password != password2:
        return RedirectResponse("../settings?error=match", status_code=302)

    if email != user.email and models.User.objects(Q(email=email)):
        return RedirectResponse("/settings?error=email", status_code=302)

    if not re.fullmatch("0?5\d{8}", phone):
        return RedirectResponse("/settings?error=phone", status_code=302)

    if password and not re.fullmatch("[A-Za-z0-9@#$%^&+=]{8,16}", password):
        return RedirectResponse("/settings?error=password", status_code=302)

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.phone = phone
    restaurant.location = location
    if password:
        user.password = get_password_hash(password)
    user.save()
    restaurant.save()

    return RedirectResponse("../settings", status_code=302)

def extract_sales(file):
    pass





@router.post("/upload")
def upload_file(file: UploadFile = File(),  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    try:
        orders = models.Orders.objects.get(user_id=ObjectId(authorize.get_jwt_subject()))

        content = file.file.read()

        buffer = StringIO(content.decode("utf-8"))

        csv_reader = csv.reader(buffer)
        for row in csv_reader:
            element_id, quantity, time = row[:3]
            orders.add_or_update_sale_to_order(datetime.strptime(time, "%m/%d/%Y").date(), element_id, float(quantity))
        orders.save()
    except Exception as e:
        print(e)
        return RedirectResponse("/upload?error=file", status_code=302)

    return RedirectResponse("/upload", status_code=302)
