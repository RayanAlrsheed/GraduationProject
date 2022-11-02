import os
from json import loads
from bson import ObjectId
from fastapi import FastAPI, Depends, Request
# from CONFIG import CONNECTION_URL
from mongoengine import connect
from starlette.responses import RedirectResponse
import models
from auth import AuthHandler
from datetime import date
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from schemas import Settings
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from API import router as api_router


app = FastAPI()
app.include_router(api_router)
CONNECTION_URL = os.environ.get("CONNECTION_URL")

connect(db='GraduationProject', host=CONNECTION_URL)

authHandler = AuthHandler()

app.mount("/static", StaticFiles(directory="assets/main"), name="static")
app.mount("/auth_static", StaticFiles(directory="assets/auth"), name="auth_static")
templates = Jinja2Templates(directory="html")


@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
async def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    print(exc)
    return RedirectResponse("/login", status_code=302)


def from_document_to_dict(document):
    json = document.to_json()
    return loads(json)


@app.get("/register")
async def register_page(request: Request, error=None):
    load = {"request": request}
    if error == "empty":

        load["message"] = "please fill the form completely"

    elif error == "email":
        load["message"] = "email already registered"

    elif error == "password":
        load["message"] = "please use a stronger password"

    elif error == "match":
        load["message"] = "passwords does not match"

    elif error == "phone":
        load["message"] = "please enter your phone number correctly"

    return templates.TemplateResponse("Sinup.html", load)

@app.get("/login")
async def login_page(request: Request, error=None):
    load = {"request": request}
    if error == "email":

        load["message"] = "email not found"
    elif error == "password":
        load["message"] = "wrong password"
    return templates.TemplateResponse("login.html", load)

@app.get("/logout")
async def logout(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    authorize.unset_jwt_cookies()

    return RedirectResponse("/login")

@app.get("/")
async def main_page(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name


    orders = models.Orders.objects.get(user_id=ObjectId(authorize.get_jwt_subject()))
    if not user.is_admin():
        monthly_labels, monthly_sales = orders.get_monthly_sales()

        weekly_labels, weekly_sales = orders.get_most_sales_in_week()

        return templates.TemplateResponse("index.html", {"request": request,
                                                         "first_name": first_name,
                                                         "last_name": last_name,
                                                         "monthly_labels": monthly_labels,
                                                         "monthly_sales": monthly_sales,
                                                         "weekly_labels": weekly_labels,
                                                         "weekly_sales": weekly_sales
                                                         })

    charity_list = models.Charity.objects.all()
    charity_list = from_document_to_dict(charity_list)
    for charity in charity_list:
        charity["_id"] = charity["_id"]["$oid"]

    return templates.TemplateResponse("charity_admin.html", {"request": request,
                                                         "first_name": first_name,
                                                         "last_name": last_name,
                                                        "charities": charity_list})


@app.get("/add_charity")
async def add_charity(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user = models.User.objects.get(id=authorize.get_jwt_subject())
    if not user.is_admin():
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse("add_charity_admin.html", {"request":request, "first_name":user.first_name, "last_name":user.last_name})


@app.get("/edit_charity")
async def edit_charity(request: Request, id=None, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user = models.User.objects.get(id=authorize.get_jwt_subject())
    if not user.is_admin():
        return RedirectResponse("/", status_code=302)

    try:
        charity = models.Charity.objects.get(id=ObjectId(id))
    except:
        return RedirectResponse("/", status_code=302)

    charity = from_document_to_dict(charity)
    charity["id"] = charity["_id"]["$oid"]

    load = {"request":request, "first_name":user.first_name, "last_name":user.last_name, "charity":charity, "edit":True}
    return templates.TemplateResponse("add_charity_admin.html", load)

@app.get("/charity")
async def charities(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name
    if not user.is_admin():
        user_id = ObjectId(authorize.get_jwt_subject())
        try:
            restaurant_location = models.Restaurant.objects.get(user_id=user_id).location
        except:
            return RedirectResponse("/")




        near_charities = models.Charity.objects(location=restaurant_location)
        charity_list = from_document_to_dict(near_charities)
        return templates.TemplateResponse("Charity.html", {"request":request, "charities": charity_list, "first_name": first_name, "last_name": last_name})


@app.get("/menu")
async def menu(request:Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    user_id = authorize.get_jwt_subject()
    try:
        menu_as_documents = models.Restaurant.objects.get(user_id=user_id).menu
    except:
        return RedirectResponse("/")

    menu_list = []
    for i, element in enumerate(menu_as_documents):
        menu_list.append(from_document_to_dict(element))
    return templates.TemplateResponse("Menu.html", {"request":request, "elements": menu_list, "first_name": first_name, "last_name": last_name})

@app.get("/menu/add")
async def add_element(request:Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    return templates.TemplateResponse("add_menu.html", {"request":request, "first_name": first_name, "last_name": last_name})


@app.get("/menu/edit")
async def edit_element(request:Request, authorize: AuthJWT = Depends(), element_id=None):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    user_id = ObjectId(authorize.get_jwt_subject())
    if not element_id:
        return RedirectResponse("/menu")

    try:
        restaurant = models.Restaurant.objects.get(user_id=user_id)
    except:
        return RedirectResponse("/")

    element = from_document_to_dict(restaurant.get_element(element_id))
    for i, ingredient in enumerate(element["ingredients"]):
        ingredient['number'] = i
    return templates.TemplateResponse("edit_menu.html", {"request":request, "element": element, "first_name": first_name, "last_name": last_name})


@app.get("/edit_ingredient")
async def edit_ingredient(request:Request, authorize: AuthJWT = Depends(), element_id=None, number:int=None):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    user_id = ObjectId(authorize.get_jwt_subject())
    if not element_id:
        return RedirectResponse("/menu")
    try:
        restaurant = models.Restaurant.objects.get(user_id=user_id)
    except:
        return RedirectResponse("/")

    ingredient = from_document_to_dict(restaurant.get_element(element_id))["ingredients"][number]

    return templates.TemplateResponse("edit_ingredient.html", {"request":request, "ingredient": ingredient, "element_id": element_id, "number":number,
                                                               "first_name": first_name, "last_name": last_name})


@app.get("/sales")
async def sales(request:Request, authorize: AuthJWT = Depends(), time: date=None):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    user_id = ObjectId(authorize.get_jwt_subject())
    load = {"request":request,  "first_name": first_name, "last_name": last_name}
    if time:
        try:
            load["time"] = time
            try:
                all_orders = models.Orders.objects.get(user_id=user_id)
            except:
                return RedirectResponse("/")


        except:
            all_orders = models.Orders(user_id=user_id)
            all_orders.save()

        orders = all_orders.get_order(time)
        if orders:
            sales = []

            for sale in orders.sales:
                sales.append(from_document_to_dict(sale))

            if sales:
                load["sales"] = sales

            unused_elements = orders.get_unused_elements()

            if unused_elements:
                load["unused"] = unused_elements
        else:

            try:
                restaurant = models.Restaurant.objects.get(user_id=user_id)
            except:
                return RedirectResponse("/")

            unused_elements = restaurant.get_all_elements_id()

            if unused_elements:
                load["unused"] = unused_elements

    return templates.TemplateResponse("sales.html", load)

@app.get("/edit_sale")
async def edit_sale(request:Request, authorize: AuthJWT = Depends(), time: date=None, element_id=None):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    user_id = ObjectId(authorize.get_jwt_subject())

    if not (time and element_id):
        return RedirectResponse(f"sales?time={time}")

    try:
        orders = models.Orders.objects.get(user_id=user_id)
    except:
        return RedirectResponse("/")

    order = orders.get_order(time)

    sale = order.get_sale(element_id)

    if not sale:
        return RedirectResponse(f"sales?time={time}")

    load = {"request":request, "element_id": element_id, "quantity": sale.quantity, "time": time,
            "first_name": first_name, "last_name": last_name
            }

    return templates.TemplateResponse("edit_sale.html", load)


@app.get("/upload")
async def upload(request:Request, authorize: AuthJWT = Depends(), error=None):
    authorize.jwt_required()

    user = models.User.objects.get(id=authorize.get_jwt_subject())
    first_name = user.first_name
    last_name = user.last_name

    load = {"request": request, "first_name": first_name, "last_name": last_name}
    if error:
        load["message"] = "Make sure that the columns are in order\\nid, quantity, date\\n and the file is saved in csv utf-8 format"
    return templates.TemplateResponse("upload.html", load)

@app.get("/settings")
async def settings(request: Request, authorize: AuthJWT = Depends(), error = None):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    try:
        user = models.User.objects.get(id=user_id)
        restaurant = models.Restaurant.objects.get(user_id=ObjectId(user_id))
    except:
        return RedirectResponse("/")

    load = {
        'request': request,
        'first_name': user.first_name,
        'last_name': user.last_name,
        "phone":user.phone,
        'email':user.email,
        'location':restaurant.location
    }

    if error == "empty":

        load["message"] = "please fill the form completely"

    elif error == "email":
        load["message"] = "email already registered"

    elif error == "password":
        load["message"] = "please use a stronger password"

    elif error == "match":
        load["message"] = "passwords does not match"

    elif error == "phone":
        load["message"] = "please enter your phone number correctly"

    return templates.TemplateResponse("Settings.html", load)
