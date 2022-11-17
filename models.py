from datetime import date, timedelta, datetime
from mongoengine import Document, StringField, ListField, FloatField, DateField, DateTimeField,EmbeddedDocumentField, EmbeddedDocument, ObjectIdField
from tensorflow import keras

model = keras.models.load_model("dnn_model")

holidays = [
    {"start": "21/09/2021", "end": "22/09/2021"},
    {"start": "17/10/2021", "end": "18/10/2021"},
    {"start": "04/11/2021", "end": "04/11/2021"},
    {"start": "25/12/2021", "end": "05/12/2021"},
    {"start": "06/01/2022", "end": "15/01/2022"},
    {"start": "02/02/2022", "end": "03/02/2022"},
    {"start": "23/02/2022", "end": "24/02/2022"},
    {"start": "10/03/2022", "end": "19/03/2022"},
    {"start": "25/04/2022", "end": "07/05/2022"},
    {"start": "16/06/2022", "end": "27/08/2022"},
    {"start": "21/09/2022", "end": "22/09/2022"},
    {"start": "10/11/2022", "end": "11/11/2022"},
    {"start": "24/11/2022", "end": "03/12/2022"},
    {"start": "18/12/2022", "end": "18/12/2022"},
    {"start": "15/01/2023", "end": "16/01/2023"},
    {"start": "22/02/2023", "end": "23/02/2023"},
    {"start": "02/03/2023", "end": "12/03/2023"},
    {"start": "13/04/2023", "end": "25/04/2023"},
    {"start": "28/05/2023", "end": "29/05/2023"},
    {"start": "22/06/2023", "end": "21/08/2023"},
]

element_ids = {
    "sk-0003": 4,
    "sk-0004": 5,
    "sk-0005": 6,
    "sk-0009": 7,
    "sk-0012": 8,
    "sk-0015": 9,
    "sk-0016": 10,
    "sk-0017": 11,
    "sk-0195": 12,
    "sk-0602": 13
}


def _is_holiday(time):
    for holiday in holidays:
        if datetime.strptime(holiday["start"], "%d/%m/%Y").date() <= time <= datetime.strptime(holiday["end"], "%d/%m/%Y").date():
            return 1
    return 0

class User(Document):
    first_name = StringField()
    last_name = StringField()
    email = StringField(unique=True)
    password = StringField()
    type = StringField()
    phone = StringField()
    created_at = DateTimeField()

    def is_admin(self):
        return self.type.lower() == "admin"


class Ingredient(EmbeddedDocument):
    name = StringField()
    quantity = FloatField()
    unit = StringField()


class Element(EmbeddedDocument):
    element_id = StringField()
    name = StringField()
    ingredients = ListField(EmbeddedDocumentField(Ingredient))

    def add_ingredient(self, name, quantity, unit):

        for ingredient in self.ingredients:
            if name == ingredient.name:
                return False

        ingredient = Ingredient(name=name, quantity=quantity, unit=unit)

        self.ingredients.append(ingredient)
        self._instance.save()
        return True

    def modify_ingredient(self, number, name, quantity, unit):
        if number >= len(self.ingredients):
            return False

        ingredient = self.ingredients[number]

        ingredient.name = name
        ingredient.unit = unit
        ingredient.quantity = quantity

        self._instance.save()

        return True

    def remove_ingredient(self, number):
        if number >= len(self.ingredients):
            return False

        ingredient = self.ingredients[number]

        self.ingredients.remove(ingredient)

        self._instance.save()
        return True


class Restaurant(Document):
    user_id = ObjectIdField()
    location = StringField()
    menu = ListField(EmbeddedDocumentField(Element))

    def add_element(self, element_id, name):
        for element in self.menu:
            if element.element_id == element_id:
                return False

        element = Element(element_id=element_id, name=name)

        self.menu.append(element)

        self.save()
        return True

    def modify_element(self, element_id_before,element_id, name=None):

        for element in self.menu:
            if element.element_id == element_id_before:
                if name:
                    element.element_id = element_id
                    element.name = name
                self.save()
                return True

        return False

    def remove_element(self, element_id):
        for element in self.menu:
            if element.element_id == element_id:
                self.menu.remove(element)
                self.save()
                return True
        return False

    def get_element(self, element_id):
        for element in self.menu:
            if element.element_id == element_id:
                return element
        return None

    def get_all_elements_id(self):
        elements = []
        for element in self.menu:
            elements.append(element.element_id)
        return elements

    def add_ingredient(self, element_id, name, quantity, unit):
        for element in self.menu:
            if element.element_id == element_id:
                return element.add_ingredient(name, quantity, unit)
        return False

    def modify_ingredient(self, element_id, number, name, quantity, unit):
        for element in self.menu:
            if element.element_id == element_id:
                return element.modify_ingredient(number, name, quantity, unit)
        return False

    def remove_ingredient(self, element_id, number):
        for element in self.menu:
            if element.element_id == element_id:
                return element.remove_ingredient(number)
        return False


class Sales(EmbeddedDocument):
    element_id = StringField()
    quantity = FloatField()


class Order(EmbeddedDocument):
    sales = ListField(EmbeddedDocumentField(Sales))
    date = DateField()

    def add_sale(self, element_id, quantity):
        for sale in self.sales:
            if sale.element_id == element_id:
                return False

        element = Sales(element_id=element_id, quantity=quantity)
        self.sales.append(element)

        return True

    def modify_sale(self, element_id, quantity=None):

        for sale in self.sales:
            if sale.element_id == element_id:
                if quantity:
                    sale.quantity = quantity
                return True
        return False

    def remove_sale(self, element_id):
        for sale in self.sales:
            if sale.element_id == element_id:
                self.sales.remove(sale)
                return True
        return False

    def get_sale(self, element_id):
        for sale in self.sales:
            if sale.element_id == element_id:
                return sale
        return None

    def _is_element_in_sales(self, element_id):
        for element in self.sales:
            if element.element_id == element_id:
                return True
        return False

    def get_unused_elements(self):
        user_id = self._instance.user_id

        restaurant = Restaurant.objects.get(user_id=user_id)

        elements = []
        for element in restaurant.menu:
            if not self._is_element_in_sales(element.element_id):
                elements.append(element.element_id)

        return elements


class Orders(Document):
    user_id = ObjectIdField()
    orders = ListField(EmbeddedDocumentField(Order))

    def add_order(self, date):
        for order in self.orders:
            if order.date == date:
                return False

        order = Order(date=date)

        self.orders.append(order)

        return order

    def add_sale_to_order(self, date, element_id, quantity):

        for order in self.orders:
            if order.date == date:
                if order.add_sale(element_id, quantity):
                    self.save()
                    return True
                return False

        order = self.add_order(date)
        order.add_sale(element_id, quantity)
        self.save()

        return True

    def add_or_update_sale_to_order(self, date, element_id, quantity):

        for order in self.orders:
            if order.date == date:
                if not order.add_sale(element_id, quantity):
                    order.modify_sale(element_id, quantity)


                return True

        order = self.add_order(date)
        order.add_sale(element_id, quantity)

        return True


    def modify_order(self, date, element_id, quantity):

        for order in self.orders:
            if order.date == date:
                if order.modify_sale(element_id, quantity):
                    self.save()
                    return True

        return False

    def remove_sale_from_order(self, date, element_id):

        for order in self.orders:
            if order.date == date:
                if order.remove_sale(element_id):
                    if len(order.sales) == 0:
                        self.orders.remove(order)
                    self.save()
                    return True

        return False

    def get_order(self, time:date):
        for order in self.orders:
            if order.date == time:
                return order
        return None

    def _is_added_to_sales(self, element_id, sales):
        for sale in sales:
            if sale["element_id"] == element_id:
                return True

        return False

    def get_most_sales_in_week(self):
        time = date.today()
        sales = []
        for order in self.orders:
            if time - timedelta(days=1) >= order.date >= time - timedelta(days=7):
                day = 6 - (time - order.date).days
                for sale in order.sales:
                    if not self._is_added_to_sales(sale.element_id, sales):
                        sales.append({"element_id": sale.element_id, "sales": [0, 0, 0, 0, 0, 0, 0], "total": 0})

                    for added_sales in sales:
                        if added_sales["element_id"] == sale.element_id:
                            added_sales["sales"][day] = sale.quantity
                            added_sales["total"] += sale.quantity
                            break

        sales.sort(key= lambda sale: sale["total"], reverse=True)
        labels = [(time - timedelta(days=i + 1)).strftime("%m/%d") for i in range(6, -1, -1)]
        return labels, sales[:5]


    def get_monthly_sales(self):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # offset
        current_month = date.today().month

        labels = []
        sales = [0 for _ in range(12)]
        for i in range(12):
            labels.append(months[(current_month + i) % 12])
        starting_date = date(year=date.today().year - 1, month= current_month, day=28)

        while (starting_date + timedelta(days=1)).month == current_month:
            starting_date = starting_date + timedelta(days=1)

        for order in self.orders:
            if order.date > starting_date:
                for sale in order.sales:
                    sales[order.date.month - current_month - 1] += sale.quantity

        return labels, sales


class Prediction(Document):
    user_id = ObjectIdField()
    orders = ListField(EmbeddedDocumentField(Order))

    def get_latest_prediction(self):
        if len(self.orders) == 0:
            return None

        return max(self.orders, key=lambda order: order.date)

    def predict(self):

        orders = Orders.objects.get(user_id=self.user_id)

        latest_order = max(orders.orders, key=lambda order: order.date)
        restaurant = Restaurant.objects.get(user_id=self.user_id)
        all_elements = [element.element_id for element in restaurant.menu]
        last_week = latest_order.date - timedelta(days=6)
        today = latest_order.date + timedelta(days=1)

        try:
            last_week_sales = orders.get_order(last_week).sales
            yesterday_sales = latest_order.sales
            last_week_ids = [element.element_id for element in last_week_sales]
            yesterday_ids = [element.element_id for element in yesterday_sales]
            elements_to_predict = [element_id for element_id in all_elements if element_id in yesterday_ids and element_id in last_week_ids]

            if len(elements_to_predict) == 0:
                raise Exception
            features = [0] * 18

            #weekend
            features[0] = 1 if 3 <= today.weekday() <= 5 else 0

            #holiday
            features[1] = _is_holiday(today)

            #seasons
            year = today.year
            if date(year=year, month=9, day=23) <= today <= date(year=year, month=12, day=20):
                features[14] = 1
            elif date(year=year, month=3, day=21) <= today <= date(year=year, month=6, day=21):
                features[15] = 1
            elif date(year=year, month=6, day=21) <= today <= date(year=year, month=9, day=22):
                features[16] = 1
            else:
                features[17] = 1

            for order in self.orders:
                if order.date == today:
                    self.orders.remove(order)
                    break

            order = Order(date=today)
            for element in elements_to_predict:
                #element id:
                features[element_ids[element]] = 1

                for sale in last_week_sales:
                    if sale.element_id == element:
                        features[2] = sale.quantity

                for sale in yesterday_sales:
                    if sale.element_id == element:
                        features[3] = sale.quantity

                order.add_sale(element, round(model.predict(features), 2))
                features[element_ids[element]] = 0

            self.orders.append(order)
            self.save()
            return True

        except Exception as e:
            print(e.args)
            return False






class Charity(Document):
    name = StringField()
    phone = StringField()
    location = StringField()
    location_url = StringField()
