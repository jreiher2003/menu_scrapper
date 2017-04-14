from app import app, db 
from flask import render_template, url_for
from sqlalchemy import desc
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
    city_metro = CityMetro.query.filter_by(state_id=state_id, metro_area=False).order_by(desc(CityMetro.r_total)).all()
    canada = CityMetro.query.filter(CityMetro.state_id==state_id, CityMetro.county_id==None).order_by(desc(CityMetro.r_total)).all()
    state_name = State.query.filter_by(id=state_id).one()
    return render_template("state_page.html", url_slug_state=url_slug_state,state_name=state_name.name, state_id=state_id, county=county, city_metro=city_metro, canada=canada)


@app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_metro_id>/")
def city_page(url_slug_state,state_id,url_slug_city,city_metro_id):
    # rest = RestaurantLinks.query.filter_by(state_id=state_id, city_metro_id=city_metro_id).all()
    rest = RestaurantLinks.query.filter_by(state_id=state_id, city_metro_id=city_metro_id).join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.restaurant_links_id == RestaurantLinks.id and RestaurantLinksCusine.cusine_id == Cusine.id).all()
    state_name = State.query.filter_by(id=state_id).one()
    city_name = CityMetro.query.filter_by(id=city_metro_id).one()
    return render_template('city_page.html', url_slug_state=url_slug_state, url_slug_city=url_slug_city, state_name=state_name.name,state_id=state_id, city_name=city_name.city_name, city_metro_id=city_metro_id, rest=rest, rest_total=city_name.r_total)


@app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_metro_id>/<path:url_slug_rest>/<path:rest_id>/")
def rest_page_city(url_slug_state, state_id, url_slug_city, city_metro_id, url_slug_rest, rest_id):
    rest = RestaurantLinks.query.filter_by(id=rest_id).one()
    return render_template("rest_page.html", rest=rest)

# @app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_metro>/<int:metro_id>/<path:url_slug_rest>/<path:rest_id>/")
# def rest_page_metro(url_slug_state, state_id, url_slug_metro, metro_id, url_slug_rest, rest_id):
#     return "metro restpage"

# @app.route("/rest")
# def rest():
#     rrr = RestaurantLinks.query.join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.restaurant_links_id == RestaurantLinks.id and RestaurantLinksCusine.cusine_id == Cusine.id and RestaurantLinks.state_id==10 and RestaurantLinks.city_id==2782).all()
#     return render_template("test.html", rrr=rrr)
