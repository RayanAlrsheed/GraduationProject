from datetime import date, datetime

from mongoengine import Document, StringField, IntField, ListField, FloatField, DateField, DateTimeField,EmbeddedDocumentField, EmbeddedDocument, ObjectIdField


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
            print(element.element_id, element_id_before)
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
            print(sale.element_id, element_id)
            if sale.element_id == element_id:
                if quantity:
                    sale.quantity = quantity
                self._instance.save()
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

    def add_sale_to_order(self, date,element_id, quantity):

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
                    if not order.sales:
                        self.delete()
                    else:
                        self.save()
                    return True

        return False

    def get_order(self, time:date):
        for order in self.orders:
            if order.date == time:
                return order
        return None


class Charity(Document):
    name = StringField()
    phone = StringField()
    location = StringField()
    location_url = StringField()
