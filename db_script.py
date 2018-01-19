from models import * 

def drop_all():
    Base.metadata.drop_all(engine)
    print "all tables dropped"

def create_all():
    Base.metadata.create_all(engine)
    print "all tables created"

def state_to_restaurant_cusine():    
    County.__table__.drop(engine)
    County.__table__.create(engine)
    CityMetro.__table__.drop(engine)
    CityMetro.__table__.create(engine)
    Restaurant.__table__.drop(engine)
    Restaurant.__table__.create(engine)
    Cusine.__table__.drop(engine)
    Cusine.__table__.create(engine)
    RestaurantCusine.__table__.drop(engine)
    RestaurantCusine.__table__.create(engine)

#################################################
#################################################
def drop_menu():
    ItemAddon.__table__.drop(engine, checkfirst=True)
    ItemPrice.__table__.drop(engine, checkfirst=True)
    MenuItem.__table__.drop(engine, checkfirst=True)
    Section.__table__.drop(engine, checkfirst=True)
    Menu.__table__.drop(engine, checkfirst=True)
    RestaurantImages.__table__.drop(engine, checkfirst=True)
    RestaurantCoverImage.__table__.drop(engine, checkfirst=True)
    print "drop_menu good"

def create_menu():
    RestaurantCoverImage.__table__.create(engine, checkfirst=True)
    RestaurantImages.__table__.create(engine, checkfirst=True)
    Menu.__table__.create(engine, checkfirst=True)
    Section.__table__.create(engine, checkfirst=True)
    MenuItem.__table__.create(engine, checkfirst=True)
    ItemPrice.__table__.create(engine, checkfirst=True)
    ItemAddon.__table__.create(engine, checkfirst=True)
    print "create menu good"


if __name__ == "__main__":
    drop_menu()
    create_menu()