BEGIN TRANSACTION;
CREATE TABLE state (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	abbr VARCHAR, 
	state_link VARCHAR, 
	PRIMARY KEY (id)
);
CREATE TABLE metro_assoc (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	metro_link VARCHAR, 
	state_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(state_id) REFERENCES state (id)
);
CREATE TABLE county (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	state_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(state_id) REFERENCES state (id)
);
CREATE TABLE city_metro (
	id INTEGER NOT NULL, 
	city_name VARCHAR, 
	neighborhood_name VARCHAR, 
	city_link VARCHAR, 
	metro_area BOOLEAN, 
	r_total INTEGER, 
	state_id INTEGER, 
	county_id INTEGER, 
	PRIMARY KEY (id),  
	FOREIGN KEY(state_id) REFERENCES state (id), 
	FOREIGN KEY(county_id) REFERENCES county (id)
);
CREATE TABLE restaurant_links (
	id INTEGER NOT NULL, 
	rest_name VARCHAR, 
	rest_link VARCHAR, 
	thumbnail_img VARCHAR, 
	menu_available BOOLEAN, 
	text_menu_available BOOLEAN, 
	city_name VARCHAR, 
	neighborhood_name VARCHAR, 
	phone VARCHAR, 
	address VARCHAR, 
	city_ VARCHAR, 
	state_ VARCHAR, 
	zip_ VARCHAR, 
	website VARCHAR, 
	description VARCHAR, 
	hours VARCHAR, 
	delivery BOOLEAN, 
	wifi BOOLEAN, 
	alcohol VARCHAR, 
	price_point VARCHAR, 
	attire VARCHAR, 
	payment VARCHAR, 
	parking VARCHAR, 
	outdoor_seats BOOLEAN, 
	reservations BOOLEAN, 
	good_for_kids BOOLEAN, 
	menu_url_id VARCHAR, 
	menu_link_pdf VARCHAR, 
	state_id INTEGER, 
	county_id INTEGER, 
	city_metro_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(state_id) REFERENCES state (id), 
	FOREIGN KEY(county_id) REFERENCES county (id), 
	FOREIGN KEY(city_metro_id) REFERENCES city_metro (id)
);
CREATE INDEX ix_restaurant_links_state_id ON restaurant_links (state_id);
CREATE INDEX ix_restaurant_links_county_id ON restaurant_links (county_id);
CREATE INDEX ix_restaurant_links_city_metro_id ON restaurant_links (city_metro_id);
CREATE INDEX ix_metro_assoc_state_id ON metro_assoc (state_id);
CREATE INDEX ix_county_state_id ON county (state_id);
CREATE INDEX ix_city_metro_state_id ON city_metro (state_id);
CREATE INDEX ix_city_metro_county_id ON city_metro (county_id);
COMMIT;
