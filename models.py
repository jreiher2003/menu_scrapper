from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///my_menu.db', echo=True)
Base = declarative_base()

class State(Base):
    __tablename__ = "state"

    id = Column(Integer, primary_key=True)
    name = Column(String)

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

    state_id = Column(Integer, ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys=state_id)

    county_id = Column(Integer, ForeignKey("county.id"), index=True)
    county = relationship("County", foreign_keys=county_id) 



# Base.metadata.drop_all(engine)
# print "all tables dropped"
# Base.metadata.create_all(engine)
# print "all tables created"





# class Province(Base):
#     __tablename__ = "providence" 

#     id = Column(Integer, primary_key=True)
#     name = Column(String)