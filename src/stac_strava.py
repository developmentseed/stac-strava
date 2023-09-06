import os
import json

import pandas as pd

from utils import ensure_directory_exists, extract_coordinates, unzip_folder


def activities_to_stac(
    file_path,
    link_file,
    collection_link,
    catalog_link,
    path_to_items,
    activity_data,
    file_type,
):
    # Extract coordinates from the file based on its type.
    coordinates = extract_coordinates(file_path, file_type)

    item_id = str(activity_data["Activity ID"])
    stac_item = {
        "id": item_id,
        "type": "Feature",
        "stac_version": "1.0.0-beta.2",
        "stac_extensions": [],
        "collection": collection_link.split("/")[-1],
        "geometry": {"type": "LineString", "coordinates": coordinates},
        "properties": {
            "name": activity_data["Activity Name"],
            "type": activity_data["Activity Type"],
            "date": activity_data["Activity Date"],
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
            {"rel": "collection", "href": collection_link},
            {"rel": "root", "href": catalog_link},
        ],
    }
    return stac_item


def activities_to_stac_catalog(
    csv_path, activities_folder, destination_folder, collection_link, catalog_link
):
    ensure_directory_exists(destination_folder)
    activities_df = pd.read_csv(csv_path)
    generated_files_count = 0

    for _, row in activities_df.iterrows():
        try:
            file_name = row["Filename"].split("/")[-1]
        except AttributeError:
            continue

        file_path = os.path.join(activities_folder, file_name)
        file_type = file_name.split(".")[-1]

        if file_type.endswith("gz"):
            file_path, file_type = unzip_folder(file_path, file_name)

        if os.path.exists(file_path):
            stac_item = activities_to_stac(
                file_path,
                file_path,
                collection_link,
                catalog_link,
                destination_folder,
                row,
                file_type,
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

    return generated_files_count
