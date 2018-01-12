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
    city_metro = City.query.filter_by(state_id=state_id, metro_area=False).order_by(desc(City.r_total)).all()
    canada = City.query.filter(City.state_id==state_id, City.county_id==None).order_by(desc(City.r_total)).all()
    state_name = State.query.filter_by(id=state_id).one()
    return render_template("state_page.html", url_slug_state=url_slug_state,state_name=state_name.name, state_id=state_id, county=county, city_metro=city_metro, canada=canada)


@app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_id>/<int:page>")
def city_page(url_slug_state,state_id,url_slug_city,city_id, page=1):
    # rest = RestaurantLinks.query.filter_by(state_id=state_id, city_metro_id=city_metro_id).all()
    rest = Restaurant.query.filter_by(state_id=state_id, city_id=city_id).order_by(asc(Restaurant.rest_name)).paginate(page, 40, False)
    state_name = State.query.filter_by(id=state_id).one()
    city_name = City.query.filter_by(id=city_id).one()
    rc = Restaurant.query.filter_by(state_id=state_id, city_id=city_id).all()
    rest_cusine1 = []      
    for r in rc:
        for j in r.rlc:
            pass
        for x in r.cusine:
            rest_cusine1.append([x.name, x.url_slug_cusine, x.id]) 
    k = sorted(rest_cusine1)
    rest_cusine = [k[i] for i in range(len(k)) if i == 0 or k[i] != k[i-1]]# removes dups 
    return render_template('city_page.html', url_slug_state=url_slug_state, url_slug_city=url_slug_city, state_name=state_name.name,state_id=state_id, city_name=city_name.city_name, city_id=city_id, rest=rest, rest_cusine=rest_cusine, rest_total=city_name.r_total)


@app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_city>/<int:city_id>/<path:url_slug_rest>/<path:rest_id>/")
def rest_page_city(url_slug_state, state_id, url_slug_city, city_id, url_slug_rest, rest_id):
    rest = Restaurant.query.filter_by(id=rest_id).one()
    return render_template("rest_page.html", rest=rest)

# @app.route("/<path:url_slug_state>/<int:state_id>/<path:url_slug_metro>/<int:metro_id>/<path:url_slug_rest>/<path:rest_id>/")
# def rest_page_metro(url_slug_state, state_id, url_slug_metro, metro_id, url_slug_rest, rest_id):
#     return "metro restpage"

# @app.route("/rest")
# def rest():
#     rrr = RestaurantLinks.query.join(RestaurantLinksCusine).join(Cusine).filter(RestaurantLinksCusine.restaurant_links_id == RestaurantLinks.id and RestaurantLinksCusine.cusine_id == Cusine.id and RestaurantLinks.state_id==10 and RestaurantLinks.city_id==2782).all()
#     return render_template("test.html", rrr=rrr)
