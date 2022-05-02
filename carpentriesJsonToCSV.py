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
from pprint import pprint

INSTRUCTOR_JSON = "https://feeds.carpentries.org/all_badged_people.json"
OUTFILE = "aunz-instructors.csv"


def get_file(jsonfile):
    response = requests.get(jsonfile)
    response.raise_for_status()
    data = response.json()
    return data


@click.command()
@click.option(
    "--country", default=["AU", "NZ"], help="Country to filter for", multiple=True
)
def main(country):

    matching_instructors = []
    instructor_data = get_file(INSTRUCTOR_JSON)
    for instructor in instructor_data:
        if instructor["country"] in country:
            # pprint(instructor)
            matching_instructors.append(instructor)
    with open(OUTFILE, "w") as destfile:
        csvwriter = csv.DictWriter(destfile, fieldnames=matching_instructors[0].keys())
        csvwriter.writeheader()
        csvwriter.writerows(matching_instructors)


if __name__ == "__main__":
    main()
