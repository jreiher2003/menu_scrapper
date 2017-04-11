from app import app, db 
from flask import render_template, url_for
from .models import * 

@app.route("/")
def index():
    state = State.query.all()
    return render_template(
        "index.html",
         state=state)

@app.route("/<path:url_slug_state>/<int:state_id>/")
def state_page(url_slug_state,state_id):
    county = County.query.filter_by(state_id=state_id).all()
    city_metro = CityMetro.query.filter_by(state_id=state_id, metro_area=False).all()
    city_metro_non_county_id = CityMetro.query.filter(CityMetro.state_id==state_id, CityMetro.county_id==None).all()
    state_name = State.query.filter_by(id=state_id).one()
    return render_template("state_page.html", url_slug_state=url_slug_state,state_name=state_name.name, state_id=state_id, county=county, city_metro=city_metro,city_metro_non_county_id=city_metro_non_county_id)

@app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_id>/")
def city_page(url_slug_state,state_id,url_slug_city,city_id):
    # rest = RestaurantLinks.query.filter_by(state_id=state_id, city_id=city_id).all()
    rest = RestaurantLinks.query.join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.restaurant_links_id == RestaurantLinks.id and RestaurantLinksCusine.cusine_id == Cusine.id and RestaurantLinks.state_id==state_id and RestaurantLinks.city_id==city_id).all()
    state_name = State.query.filter_by(id=state_id).one()
    city_name = City.query.filter_by(id=city_id).one()
    return render_template('city_page.html', url_slug_state=url_slug_state, url_slug_city=url_slug_city, state_name=state_name.name,state_id=state_id, city_name=city_name.name, city_id=city_id, rest=rest)

# @app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_metro>/<int:metro_id>/")
# def metro_page(url_slug_state,state_id,url_slug_metro,metro_id):
#     # rest = RestaurantLinks.query.filter_by(state_id=state_id, city_id=city_id).all()
#     rest = RestaurantLinks.query.join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.restaurant_links_id == RestaurantLinks.id and RestaurantLinksCusine.cusine_id == Cusine.id and RestaurantLinks.state_id==state_id and RestaurantLinks.metro_area_id==metro_id).all()
#     state_name = State.query.filter_by(id=state_id).one()
#     metro_name = MetroArea.query.filter_by(id=metro_id).one()
#     print metro_name.neighborhood_name
#     print metro_name.id
#     return render_template('metro_page.html', url_slug_state=url_slug_state, url_slug_city=url_slug_city, state_name=state_name.name,state_id=state_id, metro_name=metro_name, city_id=city_id, rest=rest)

# @app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_id>/<path:url_slug_rest>/<path:rest_id>/")
# def rest_page_city(url_slug_state, state_id, url_slug_city, city_id, url_slug_rest, rest_id):
#     return "city restpage"

# @app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_metro>/<int:metro_id>/<path:url_slug_rest>/<path:rest_id>/")
# def rest_page_metro(url_slug_state, state_id, url_slug_metro, metro_id, url_slug_rest, rest_id):
#     return "metro restpage"

# @app.route("/rest")
# def rest():
#     rrr = RestaurantLinks.query.join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.restaurant_links_id == RestaurantLinks.id and RestaurantLinksCusine.cusine_id == Cusine.id and RestaurantLinks.state_id==10 and RestaurantLinks.city_id==2782).all()
#     return render_template("test.html", rrr=rrr)
