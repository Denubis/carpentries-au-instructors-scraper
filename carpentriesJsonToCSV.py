#!/usr/bin/env python3
"""
Parser to filter the carpentries 
https://feeds.carpentries.org/all_badged_people.json for AUNZ instructors 
and emit to CSV. 

Apache 2 License. Brian Ballsun-Stanton
"""

import requests
import json
import csv
import click
import re
from countryboundingboxes import bounding_boxes
from collections import defaultdict
from pprint import pprint

INSTRUCTOR_JSON = "https://feeds.carpentries.org/all_badged_people.json"
AIRPORTS_GEOJSON = "https://feeds.carpentries.org/all_instructors_by_airport.json"
AIRPORT_STATES = "https://github.com/algolia/datasets/raw/master/airports/airports.json"
OUTFILE = "aunz-instructors.csv"


def get_file(jsonfile):
    response = requests.get(jsonfile)
    response.raise_for_status()
    data = response.json()
    return data


def make_initials(name):
    """Render someone's name by initials by taking the first letter of each word-space"""

    initials = []
    for word in re.split(r"[ -]", name):
        if word:
            initials.append(word[0].upper())
    if initials:
        # print(name, initials)
        return "".join(initials)
    else:
        return None


@click.command()
@click.option(
    "--country", default=["AU", "NZ"], help="Country to filter for", multiple=True
)
def main(country):

    matching_instructors = []
    instructor_data = get_file(INSTRUCTOR_JSON)
    airport_data = get_file(AIRPORTS_GEOJSON)
    airport_states_json = get_file(AIRPORT_STATES)
    # airport_states = list(
    # filter(lambda d: d["iata_code"] in country, airport_states_json)
    # )
    airport_states = {}

    initials_by_airport = defaultdict(list)
    initials_by_state = defaultdict(list)
    for airport in airport_data:
        target_lat = airport["airport_latitude"]
        target_long = airport["airport_longitude"]
        for country_box_key, country_box in bounding_boxes(country).items():
            if (
                target_long >= country_box[1][0]
                and target_long <= country_box[1][2]
                and target_lat >= country_box[1][1]
                and target_lat <= country_box[1][3]
            ):
                for airport_state in airport_states_json:

                    if airport_state["iata_code"] == airport["airport_code"]:
                        city = airport_state["city"]
                print(airport["airport_code"], target_long, target_lat, country_box)
                # print(airport)
                for initials in airport["instructors"]:
                    initials_by_airport[initials + country_box_key].append(
                        airport["airport_code"]
                    )
                    initials_by_state[initials + country_box_key].append(
                        f"{city}, {country_box_key}"
                    )

    for instructor in instructor_data:
        if instructor["country"] in country:
            # pprint(instructor)
            instructor["initials"] = make_initials(instructor["person_name"])
            instructor["matching_airports"] = ";".join(
                initials_by_airport[instructor["initials"] + instructor["country"]]
            )
            instructor["matching_cities"] = ";".join(
                initials_by_state[instructor["initials"] + instructor["country"]]
            )
            matching_instructors.append(instructor)
    with open(OUTFILE, "w", newline="") as destfile:
        csvwriter = csv.DictWriter(destfile, fieldnames=matching_instructors[0].keys())
        csvwriter.writeheader()
        csvwriter.writerows(matching_instructors)


if __name__ == "__main__":
    main()
