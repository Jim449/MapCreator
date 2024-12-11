import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


class Database():
    def __init__(self):
        load_dotenv()
        self.database = os.getenv("DATABASE")
        self.password = os.getenv("PASSWORD")

    def get_connection(self):
        return psycopg2.connect(
            database=self.database,
            password=self.password,
            user="postgres",
            host="localhost",
            port="5432")

    def new_map(self, connection, radius: int):
        drop_query = """
DROP TABLE IF EXISTS precision;
DROP TABLE IF EXISTS terrain;
DROP TABLE IF EXISTS plates;
DROP TABLE IF EXISTS lines;
DROP TABLE IF EXISTS boundaries;
DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS cities;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS square_kilometers;
DROP TABLE IF EXISTS square_miles;
DROP TABLE IF EXISTS region_metrics;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS subregions;
DROP TABLE IF EXISTS world;
"""
        world_query = """
CREATE TABLE world (
id SMALLSERIAL PRIMARY KEY,
radius SMALLINT NOT NULL);
"""
        terrain_query = """
CREATE TABLE terrain (
id SMALLSERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL UNIQUE);
"""
        region_metrics_query = """
CREATE TABLE region_metrics (
id SMALLSERIAL PRIMARY KEY,
area INT NOT NULL,
top_stretch SMALLINT NOT NULL,
bottom_stretch SMALLINT NOT NULL,
vertical_stretch SMALLINT NOT NULL,
cost DECIMAL NOT NULL,
y SMALLINT NOT NULL,
length_division SMALLINT NOT NULL);
"""
        plate_query = """
CREATE TABLE plates (
id SMALLSERIAL PRIMARY KEY);
"""
        region_query = """
CREATE TABLE regions (
id SMALLSERIAL PRIMARY KEY,
x SMALLINT NOT NULL,
y SMALLINT NOT NULL,
metrics_id REFERENCES region_metrics(id) NOT NULL);
"""
        subregion_query = """
CREATE TABLE subregions (
id SERIAL PRIMARY KEY,
x SMALLINT NOT NULL,
y SMALLINT NOT NULL,
terrain_id SMALLINT REFERENCES terrain(id) NOT NULL,
metrics_id SMALLINT REFERENCES region_metrics(id) NOT NULL,
plate_id SMALLINT REFERENCES plates(id));
"""
        square_mile_query = """
CREATE TABLE square miles (
id SERIAL PRIMARY KEY,
x SMALLINT NOT NULL,
y SMALLINT NOT NULL,
terrain_id SMALLINT REFERENCES terrain(id),
region_id SMALLINT REFERENCES regions(id) NOT NULL;
"""
        square_kilometer_query = """
CREATE TABLE square_kilometers (
id BIGSERIAL PRIMARY KEY,
x SMALLINT NOT NULL,
y SMALLINT NOT NULL,
terrain_id SMALLINT REFERENCES terrain(id) NOT NULL,
region_id SMALLINT REFERENCES regions(id) NOT NULL);
"""
        world_insert_query = """
INSERT INTO world (radius)
VALUES (%s);
"""
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(world_query)
                cursor.execute(terrain_query)
                cursor.execute(region_metrics_query)
                cursor.execute(plate_query)
                cursor.execute(region_query)
                cursor.execute(subregion_query)
                cursor.execute(square_mile_query)
                cursor.execute(square_kilometer_query)
                cursor.execute(world_insert_query, radius)

    #     precision_query = """
    # CREATE TABLE precision (
    # id SMALLSERIAL PRIMARY KEY,
    # name VARCHAR(255) NOT NULL UNIQUE);
    # """
    #     boundary_query = """
    # CREATE TABLE boundaries (
    # id SERIAL PRIMARY KEY);
    # """
    #     line_query = """
    # CREATE TABLE lines (
    # id SERIAL PRIMARY KEY,
    # boundary_id INT REFERENCES boundaries(id) NOT NULL);
    # """
    #     line_kilometer_query = """
    # CREATE TABLE line_kilometers (
    # id INT PRIMARY KEY,
    # line_id REFERENCES lines(id) NOT NULL,
    # kilometer_id REFERENCES square_kilometers(id) NOT NULL);
    # """
    #     label_query = """
    # CREATE TABLE label (
    # id SERIAL PRIMARY KEY,
    # name VARCHAR(255) NOT NULL,
    # importance SMALLINT REFERENCES precision(id) NOT NULL,
    # kilometer_id REFERENCES square_kilometers(id),
    # mile_id REFERENCES square_miles(id),
    # subregion_id REFERENCES subregions(id));
    # """
    #     city_query = """
    # CREATE TABLE cities (
    # id SERIAL PRIMARY KEY,
    # name VARCHAR(255) NOT NULL,
    # importance SMALLINT REFERENCES precision(id) NOT NULL,
    # kilometer_id REFERENCES square_kilometers(id),
    # mile_id REFERENCES square_miles(id),
    # subregion_id REFERENCES subregions(id),
    # label_id REFERENCES labels(id) NOT NULL);
    # """
    #     country_query = """
    # CREATE TABLE countries (
    # id SERIAL PRIMARY KEY,
    # name VARCHAR(255) NOT NULL UNIQUE,
    # importance SMALLINT REFERENCES precision(id) NOT NULL),
    # label_id REFERENCES labels(id) NOT NULL);
    # """

        # There's many design questions to solve
        # Hold on with some databases for now

        # Note: The user gets to decide which level of precision he works on
        # I don't want to generate all 50 million square kilometers
        # if the user doesn't even bother to zoom in to look at them
        # A city can belong to a subregion, square mile or square kilometer
        # but doesn't have to belong to all of them

        # It becomes harder when I start considering countries
        # They may have to be linked to multiple areas in multiple zoom levels

        # How about labels?
        # Should I have different labels on different zoom levels?
        # Multiple labels on the same zoom level for the same item?

    def open_area(self, x: int, y: int) -> None:
        # Opens a portion of the world
        # If I open one region, that's 6x6 subregions
        # Let's give each subregion 20x20 pixels
        # Then, each region gives 120x120
        # I can open 12x6 regions
        # If I open an area far to the east, append the west to the right
        # Something similar could be done for the north but it's harder
        pass

    def open_region(self, x: int, y: int) -> list[list[int]]:
        # Opens a region. Should be about 660x660 square kilometers
        # Return a dataframe of square kilometers?
        query = """
SELECT x, y, terrain_id FROM square_kilometers
JOIN regions ON square_kilometers.region_id = regions_id
WHERE region.x = %s AND region.y = %s;
"""
        connection = self.get_connection()

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (x, y))
                result = cursor.fetchall()
                # I may want this result in a nice format
                # Perhaps a list[list[int]]
                # I need to order by x to get each element in its correct position
                # Or should I use dataframes?
