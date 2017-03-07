from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///my_menu.db', echo=True)
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
    city_name = Column(String)
    neighborhood_name = Column(String)  

    # page 2 attributes address, phone, cusine, hours, delivery, payment, price point, wifi, attire, alcohol, comments? more photos? menu_id

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys=state_id)
    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    county = relationship("County", foreign_keys=county_id) 
    city_id = Column(Integer, ForeignKey("city.id"), index=True)
    city = relationship("City", foreign_keys=city_id)
    metro_area_id = Column(Integer, ForeignKey("metro_area.id"), index=True)
    metro_area = relationship("MetroArea", foreign_keys=metro_area_id)



# Base.metadata.drop_all(engine)
# print "all tables dropped"
# Base.metadata.create_all(engine)
# print "all tables created"

# RestaurantLinks.__table__.drop(engine)
# RestaurantLinks.__table__.create(engine)





# class Province(Base):
#     __tablename__ = "providence" 

#     id = Column(Integer, primary_key=True)
#     name = Column(String)