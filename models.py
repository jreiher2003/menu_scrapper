from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///my_menu.db')
Base = declarative_base()

class State(Base):
    __tablename__ = "state"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    abbr = Column(String)
    state_link = Column(String)

class MetroAssoc(Base):
    __tablename__ = "metro_assoc" 

    id = Column(Integer, primary_key=True)
    name = Column(String)
    metro_link = Column(String) 

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys=state_id)

class County(Base):
    __tablename__ = "county"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys=state_id) 

class City(Base):
    __tablename__ = "city" 

    id = Column(Integer, primary_key=True)
    name = Column(String)
    city_link = Column(String)
    metro_area = Column(Boolean)
    r_total = Column(Integer)

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys=state_id)
    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    county = relationship("County", foreign_keys=county_id) 

class MetroArea(Base):
    __tablename__ = "metro_area"

    id = Column(Integer, primary_key=True)
    city_name = Column(String)
    neighborhood_name = Column(String) 
    metro_link = Column(String)
    r_total = Column(Integer)

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys=state_id)
    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    county = relationship("County", foreign_keys=county_id) 
    city_id = Column(Integer, ForeignKey("city.id"), index=True)
    city = relationship("City", foreign_keys=city_id)

class RestaurantLinks(Base):
    __tablename__ = "restaurant_links"

    id = Column(Integer, primary_key=True)
    rest_name = Column(String)
    rest_link = Column(String)
    thumbnail_img = Column(String) # cdn link to img for later download 
    menu_available = Column(Boolean)
    text_menu_available = Column(Boolean)
    city_name = Column(String)
    neighborhood_name = Column(String)  
    # page 2 attributes address, phone, cusine, hours, delivery, payment, price point, wifi, attire, alcohol, comments? more photos? menu_id
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
    state = relationship("State", foreign_keys=state_id)
    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    county = relationship("County", foreign_keys=county_id) 
    city_id = Column(Integer, ForeignKey("city.id"), index=True)
    city = relationship("City", foreign_keys=city_id)
    metro_area_id = Column(Integer, ForeignKey("metro_area.id"), index=True)
    metro_area = relationship("MetroArea", foreign_keys=metro_area_id)
    cusine = relationship('Cusine', secondary='restaurant_links_cusine', backref=backref('restaurant_links', lazy='dynamic', cascade="all, delete-orphan", single_parent=True))
    menu = relationship("Menu", uselist=False, backref="restaurant_links")

class Cusine(Base):
    __tablename__ = "cusine"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class RestaurantLinksCusine(Base):
    __tablename__ = "restaurant_links_cusine"

    id = Column(Integer, primary_key=True)
    restaurant_links_id = Column(Integer, ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    cusine_id = Column(Integer, ForeignKey('cusine.id', ondelete='CASCADE'), index=True)

class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True) 
    name = Column(String)
    restaurant_links_id = Column(Integer, ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True) 
    name = Column(String)
    description = Column(String)

class RestaurantMenuCategory(Base):
    __tablename__ = "restaurant_menu_category"
    
    id = Column(Integer, primary_key=True)
    restaurant_links_id = Column(Integer, ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    menu_id = Column(Integer, ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'), index=True)

class RestaurantMenuCategoryItem(Base):
    __tablename__ = "restaurant_menu_category_item"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(String)

    restaurant_links_id = Column(Integer, ForeignKey('restaurant_links.id', ondelete='CASCADE'), index=True)
    menu_id = Column(Integer, ForeignKey('menu.id', ondelete='CASCADE'), index=True)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'), index=True)



# Base.metadata.drop_all(engine)
# print "all tables dropped"
# Base.metadata.create_all(engine)
# print "all tables created"

# RestaurantLinks.__table__.drop(engine)
# RestaurantLinks.__table__.create(engine)

# Cusine.__table__.drop(engine)
# Cusine.__table__.create(engine)

# RestaurantLinksCusine.__table__.drop(engine)
# RestaurantLinksCusine.__table__.create(engine)


#################################################
#################################################

# Menu.__table__.drop(engine)
Menu.__table__.create(engine)

# Category.__table__.drop(engine)
Category.__table__.create(engine)

# RestaurantMenuCategory.__table__.drop(engine)
RestaurantMenuCategory.__table__.create(engine)

# RestaurantMenuCategoryItem.__table__.drop(engine)
RestaurantMenuCategoryItem.__table__.create(engine)

