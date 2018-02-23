# -*- coding: utf-8 -*-
import os
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from slugify import slugify

engine = create_engine(os.environ["SCRAPER_URL_TEST"])
Base = declarative_base()

class State(Base):
    __tablename__ = "state"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    abbr = Column(String)
    counties = relationship("County")
    cities = relationship("City")
    restaurants = relationship("Restaurant")

class County(Base):
    __tablename__ = "county"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    cities = relationship("City")
    restaurants = relationship("Restaurant")
     
class City(Base):
    __tablename__ = "city" 
    id = Column(Integer, primary_key=True)
    city_name = Column(String)
    neighborhood_name = Column(String)
    metro_area = Column(Boolean)
    r_total = Column(Integer)
    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    restaurants = relationship("Restaurant")
    
class Restaurant(Base):
    __tablename__ = "restaurant"
    id = Column(Integer, primary_key=True)
    rest_name = Column(String)
    rest_link = Column(String)
    thumbnail_img = Column(String) # cdn link to img for later download 
    menu_available = Column(Boolean)
    text_menu_available = Column(Boolean)
    city_name = Column(String)
    neighborhood_name = Column(String)  
    phone = Column(String)
    address = Column(String)
    city_ = Column(String)
    state_ = Column(String)
    zip_ = Column(String)
    website = Column(String)
    description = Column(String)
    hours = Column(String)
    delivery = Column(Boolean)
    wifi = Column(Boolean)
    alcohol = Column(String)
    price_point = Column(String)
    attire = Column(String)
    payment = Column(String)
    parking = Column(String)
    outdoor_seats = Column(Boolean) 
    reservations = Column(Boolean)
    good_for_kids = Column(Boolean)
    menu_url_id = Column(String)
    menu_link_pdf = Column(String)

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    city_id = Column(Integer, ForeignKey("city.id"), index=True)
    menu = relationship("Menu")
    
class Cusine(Base):
    __tablename__ = "cusine"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class RestaurantCusine(Base):
    __tablename__ = "restaurant_cusine"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)
    cusine_id = Column(Integer, ForeignKey('cusine.id', ondelete='CASCADE'), index=True)

class RestaurantCoverImage(Base):
    __tablename__ = "restaurant_cover_image"
    id = Column(Integer, primary_key=True)
    cover_photo = Column(String)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)

class RestaurantImages(Base):
    __tablename__ = "restaurant_images"
    id = Column(Integer, primary_key=True)
    photos = Column(String)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)

class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True) 
    name = Column(String)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)
    menu_section = relationship("Section")

class Section(Base):
    __tablename__ = "section"
    id = Column(Integer, primary_key=True) 
    name = Column(String)
    description = Column(String)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)
    menu_id = Column(Integer, ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    items = relationship("MenuItem")
 
class MenuItem(Base):
    __tablename__ = "menu_item"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    menu_id = Column(Integer, ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    section_id = Column(Integer, ForeignKey('section.id', ondelete='CASCADE'), index=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)
    price_items = relationship("ItemPrice")

class ItemPrice(Base):
    __tablename__ = "item_price"
    id = Column(Integer, primary_key=True)
    price_title = Column(String)
    price_value = Column(String)
    menu_id = Column(Integer, ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    section_id = Column(Integer, ForeignKey('section.id', ondelete='CASCADE'), index=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)
    menu_item_id = Column(Integer, ForeignKey('menu_item.id', ondelete='CASCADE'), index=True) 

class ItemAddon(Base):
    __tablename__ = "item_addon"
    id = Column(Integer, primary_key=True)
    addon_title = Column(String)
    addon_value = Column(String)
    menu_id = Column(Integer, ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    section_id = Column(Integer, ForeignKey('section.id', ondelete='CASCADE'), index=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', ondelete='CASCADE'), index=True)
    menu_item_id = Column(Integer, ForeignKey('menu_item.id', ondelete='CASCADE'), index=True) 





