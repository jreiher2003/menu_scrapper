BEGIN TRANSACTION;
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
	CHECK (metro_area IN (0, 1)), 
	FOREIGN KEY(state_id) REFERENCES state (id), 
	FOREIGN KEY(county_id) REFERENCES county (id)
);
CREATE INDEX ix_restaurant_links_state_id ON restaurant_links (state_id);
CREATE INDEX ix_restaurant_links_county_id ON restaurant_links (county_id);
CREATE INDEX ix_restaurant_links_city_metro_id ON restaurant_links (city_metro_id);
CREATE INDEX ix_metro_assoc_state_id ON metro_assoc (state_id);
CREATE INDEX ix_county_state_id ON county (state_id);
CREATE INDEX ix_city_metro_state_id ON city_metro (state_id);
CREATE INDEX ix_city_metro_county_id ON city_metro (county_id);
COMMIT;
