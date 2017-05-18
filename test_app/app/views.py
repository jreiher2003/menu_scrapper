from app import app, db 
from flask import render_template, url_for
from sqlalchemy import desc, asc
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
    all_cusine_city = RestaurantLinks.query.filter_by(state_id=state_id, city_metro_id=city_metro_id).join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.cusine_id == Cusine.id).all()
    acc = []
    for a in all_cusine_city:
        for c in a.cusine:
            if c.name not in [x[0] for x in acc]:
                acc.append((c.name,c.id,c.url_slug_cusine))
    acc = sorted(acc, key=lambda x: x[0])
    return render_template('city_page.html', url_slug_state=url_slug_state, url_slug_city=url_slug_city, state_name=state_name.name,state_id=state_id, city_name=city_name.city_name, city_metro_id=city_metro_id, rest=rest, rest_total=city_name.r_total, all_cusine_city=all_cusine_city, acc=acc)

@app.route("/r/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_metro_id>/<path:url_slug_rest>/<path:rest_id>/")
def rest_page_city(url_slug_state, state_id, url_slug_city, city_metro_id, url_slug_rest, rest_id):
    rest = RestaurantLinks.query.filter_by(id=rest_id).one()
    menu_name = Menu.query.filter_by(restaurant_links_id=rest_id).one_or_none()
    cats = Menu.query.filter_by(restaurant_links_id=rest_id).join(RestaurantMenuCategory).join(Category).join(RestaurantMenuCategoryItem).filter(RestaurantMenuCategory.restaurant_links_id==rest_id and RestaurantMenuCategory.category_id==Category.id).all()
    return render_template("rest_page.html", rest=rest, menu_name=menu_name, cats=cats)

@app.route("/c/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_metro_id>/<path:url_slug_cusine>/<path:cusine_id>/")
def page_cusine_city(url_slug_state, state_id, url_slug_city, city_metro_id, url_slug_cusine, cusine_id):
    rest_c = RestaurantLinks.query.filter_by(state_id=state_id, city_metro_id=city_metro_id).join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.cusine_id == cusine_id).all()
    cusine_name = Cusine.query.filter_by(id=cusine_id).one()
    return render_template('page_cusine_city.html', rest_c=rest_c, url_slug_state=url_slug_state, state_id=state_id, url_slug_city=url_slug_city, city_metro_id=city_metro_id, url_slug_cusine=url_slug_cusine, cusine_id=cusine_id, cusine_name=cusine_name.name)




