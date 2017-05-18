import os
from app import db
from slugify import slugify

class State(db.Model):
    __tablename__ = "state"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    abbr = db.Column(db.String)
    state_link = db.Column(db.String)

    @property 
    def url_slug_state(self):
        return slugify(self.name)

class MetroAssoc(db.Model):
    __tablename__ = "metro_assoc" 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    metro_link = db.Column(db.String) 
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), index=True)
    state = db.relationship("State", foreign_keys=state_id)

class County(db.Model):
    __tablename__ = "county"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), index=True)
    state = db.relationship("State", foreign_keys=state_id) 

    @property 
    def url_slug_county(self):
        return slugify(self.name)

class CityMetro(db.Model):
    __tablename__ = "city_metro" 
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String)
    neighborhood_name = db.Column(db.String)
    city_link = db.Column(db.String)
    metro_area = db.Column(db.Boolean)
    r_total = db.Column(db.Integer)
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), index=True)
    state = db.relationship("State", foreign_keys=state_id)
    county_id = db.Column(db.Integer, db.ForeignKey("county.id"), index=True)
    county = db.relationship("County", foreign_keys=county_id) 

    @property 
    def url_slug_city(self):
        return slugify(self.city_name)


class RestaurantLinks(db.Model):
    __tablename__ = "restaurant_links"
    id = db.Column(db.Integer, primary_key=True)
    rest_name = db.Column(db.String)
    rest_link = db.Column(db.String)
    thumbnail_img = db.Column(db.String) # cdn link to img for later download 
    menu_available = db.Column(db.Boolean)
    text_menu_available = db.Column(db.Boolean)
    city_name = db.Column(db.String)
    neighborhood_name = db.Column(db.String)  
    phone = db.Column(db.String)
    address = db.Column(db.String)
    city_ = db.Column(db.String)
    state_ = db.Column(db.String)
    zip_ = db.Column(db.String)
    website = db.Column(db.String)
    description = db.Column(db.String)
    hours = db.Column(db.String)
    delivery = db.Column(db.Boolean)
    wifi = db.Column(db.Boolean)
    alcohol = db.Column(db.String)
    price_point = db.Column(db.String)
    attire = db.Column(db.String)
    payment = db.Column(db.String)
    parking = db.Column(db.String)
    outdoor_seats = db.Column(db.Boolean) 
    reservations = db.Column(db.Boolean)
    good_for_kids = db.Column(db.Boolean)
    menu_url_id = db.Column(db.String)
    menu_link_pdf = db.Column(db.String)
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), index=True)
    state = db.relationship("State", foreign_keys=state_id)
    county_id = db.Column(db.Integer, db.ForeignKey("county.id"), index=True)
    county = db.relationship("County", foreign_keys=county_id) 
    city_metro_id = db.Column(db.Integer, db.ForeignKey("city_metro.id"), index=True)
    city_metro = db.relationship("CityMetro", foreign_keys=city_metro_id)
    cusine = db.relationship('Cusine', secondary='restaurant_links_cusine', backref=db.backref('restaurant_links', lazy='dynamic', cascade="all, delete-orphan", single_parent=True))
    menu = db.relationship("Menu", uselist=False, backref="restaurant_links")

    @property 
    def url_slug_rest(self):
        if self.neighborhood_name is not None:
            return slugify(self.neighborhood_name)
        return slugify(self.rest_name)

class Cusine(db.Model):
    __tablename__ = "cusine"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    @property 
    def url_slug_cusine(self):
        return slugify(self.name)

class RestaurantLinksCusine(db.Model):
    __tablename__ = "restaurant_links_cusine"
    id = db.Column(db.Integer, primary_key=True)
    restaurant_links_id = db.Column(db.Integer, db.ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    cusine_id = db.Column(db.Integer, db.ForeignKey('cusine.id', ondelete='CASCADE'), index=True)

class Menu(db.Model):
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String)
    restaurant_links_id = db.Column(db.Integer, db.ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    category = db.relationship('Category', secondary='restaurant_menu_category', order_by='RestaurantMenuCategory.id', backref=db.backref('menu', lazy='dynamic', cascade='all, delete-orphan', single_parent=True))
    menu_item = db.relationship('RestaurantMenuCategoryItem', order_by='RestaurantMenuCategoryItem.id', backref=db.backref('menu', cascade='all, delete-orphan', single_parent=True))

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String)
    description = db.Column(db.String)

class RestaurantMenuCategory(db.Model):
    __tablename__ = "restaurant_menu_category"
    id = db.Column(db.Integer, primary_key=True)
    restaurant_links_id = db.Column(db.Integer, db.ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), index=True)

class RestaurantMenuCategoryItem(db.Model):
    __tablename__ = "restaurant_menu_category_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.String)
    restaurant_links_id = db.Column(db.Integer, db.ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), index=True)