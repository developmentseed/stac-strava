import os
import json
from datetime import datetime
import pytz
from pathlib import Path

import pandas as pd
from pystac import Collection, Extent, SpatialExtent, TemporalExtent

from utils import (
    ensure_directory_exists,
    extract_coordinates,
    unzip_folder,
    update_spatial_bounds,
)


def generate_stac_collection(
    min_lat, min_lon, max_lat, max_lon, earliest_time, latest_time, collection_id
):
    earliest_time = pytz.utc.localize(earliest_time)
    latest_time = pytz.utc.localize(latest_time)

    collection_title = "Strava Activities"
    collection_description = "This is a collection of Strava activities."
    collection_extent = Extent(
        SpatialExtent([[min_lon, min_lat, max_lon, max_lat]]),
        TemporalExtent([[earliest_time, latest_time]]),
    )
    collection = Collection(
        id=collection_id,
        title=collection_title,
        description=collection_description,
        extent=collection_extent,
        href=collection_id,
    )
    return collection


def activity_to_stac(
    file_path,
    link_file,
    collection_id,
    catalog_link,
    path_to_items,
    activity_data,
    file_type,
    min_lat,
    min_lon,
    max_lat,
    max_lon,
):
    # Extract coordinates from the file based on its type.
    coordinates = extract_coordinates(file_path, file_type)
    min_lat, min_lon, max_lat, max_lon = update_spatial_bounds(
        coordinates, min_lat, min_lon, max_lat, max_lon
    )

    date_str = activity_data["Activity Date"]
    date_obj = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
    date_obj_utc = pytz.utc.localize(date_obj)
    date_iso = date_obj_utc.isoformat()

    item_id = str(activity_data["Activity ID"])
    stac_item = {
        "id": item_id,
        "type": "Feature",
        "stac_version": "1.0.0-beta.2",
        "stac_extensions": [],
        "collection": collection_id.split("/")[-1],
        "geometry": {"type": "LineString", "coordinates": coordinates},
        "properties": {
            "name": activity_data["Activity Name"],
            "type": activity_data["Activity Type"],
            "datetime": date_iso,
            "distance": activity_data["Distance"],
        },
        "assets": {
            "data": {
                "href": link_file,
                "type": "application/xml"
                if file_type not in ["fit", "tcx"]
                else "application/octet-stream",
                "title": f"{file_type.upper()} Data",
            }
        },
        "links": [
            {"rel": "self", "href": f"{path_to_items}{item_id}.json"},
            {"rel": "collection", "href": collection_id},
            {"rel": "root", "href": catalog_link},
        ],
    }
    return stac_item, min_lat, min_lon, max_lat, max_lon


def activities_to_stac_catalog(
    csv_path, activities_folder, destination_folder, collection_id, catalog_link
):
    ensure_directory_exists(destination_folder)
    activities_df = pd.read_csv(csv_path)
    generated_files_count = 0

    min_lat, min_lon, max_lat, max_lon = 90, 180, -90, -180
    earliest_time = datetime.max
    latest_time = datetime.min

    for _, row in activities_df.iterrows():
        try:
            file_name = row["Filename"].split("/")[-1]
        except AttributeError:
            continue

        activity_datetime = datetime.strptime(
            row["Activity Date"], "%b %d, %Y, %I:%M:%S %p"
        )
        earliest_time = min(earliest_time, activity_datetime)
        latest_time = max(latest_time, activity_datetime)

        file_path = os.path.join(activities_folder, file_name)
        file_type = file_name.split(".")[-1]

        if file_type.endswith("gz"):
            file_path, file_type = unzip_folder(file_path, file_name)

        if os.path.exists(file_path):
            stac_item, min_lat, min_lon, max_lat, max_lon = activity_to_stac(
                file_path,
                file_path,
                collection_id,
                catalog_link,
                destination_folder,
                row,
                file_type,
                min_lat,
                min_lon,
                max_lat,
                max_lon,
            )

            # Check if the stac_item is None and if so, print the reason
            if not stac_item:
                print(f"Skipping {file_name} due to no coordinates extracted.")
                continue

            stac_item_path = os.path.join(destination_folder, f"{stac_item['id']}.json")
            with open(stac_item_path, "w") as file:
                json.dump(stac_item, file)
            generated_files_count += 1
            
        else:
            print(f"File {file_path} does not exist!")

    collection = generate_stac_collection(
        min_lat, min_lon, max_lat, max_lon, earliest_time, latest_time, collection_id
    )

    
    parent_path = Path(destination_folder).parent
    collection_path = os.path.join(parent_path, f"{collection_id}.json")
    print(collection_path)
    with open(collection_path, "w+") as file:
        json.dump(collection.to_dict(), file)

    return generated_files_count
