import os

import pytz
from pathlib import Path
from tqdm import tqdm
import dateparser
import pandas as pd
import pystac

from utils import extract_coordinates, unzip_folder


def activity_to_stac(
    file_path,
    link_file,
    collection,
    activity_data,
    file_type,
):
    # Extract coordinates from the file based on its type.
    coordinates = extract_coordinates(file_path, file_type)
    try:
        lon, lat = zip(*coordinates)
        bbox = [min(lon), min(lat), max(lon), max(lat)]
    except ValueError:
        bbox = None

    date_str = activity_data[1]
    date_obj = dateparser.parse(date_str)
    date_obj_utc = pytz.utc.localize(date_obj)
    item_id = str(activity_data[0])

    stac_item = pystac.Item(
        id=item_id,
        collection=collection,
        geometry={"type": "LineString", "coordinates": coordinates},
        datetime=date_obj_utc,
        bbox=bbox,
        properties={
            "name": activity_data[2],
            "type": activity_data[3],
            "datetime": date_obj_utc,
            "distance": activity_data[6],
        },
    )
    stac_item.add_asset(
        key="data",
        asset=pystac.Asset(
            href=link_file,
            media_type="application/xml"
            if file_type not in ["fit", "tcx"]
            else "application/octet-stream",
            title=f"{file_type.upper()} Data",
            roles=["data"],
        ),
    )

    # Note: stac_item.validate() will fail at this stage because of missing links
    # The links will be set automagically when we do `catalog.normalize_hrefs` later
    return stac_item


def activities_to_stac_catalog(
    csv_path,
    activities_folder,
    destination_folder,
    collection_id,
):
    catalog = pystac.Catalog(id="strava", description="Strava Activities")
    collection = pystac.Collection(
        id=collection_id,
        title="Strava Activities",
        description="This is a collection of Strava activities.",
        extent=pystac.Extent(
            spatial=None,
            temporal=None,
        ),
    )
    catalog.add_child(collection)

    activities_df = pd.read_csv(csv_path)
    generated_files_count = 0

    for _, row in tqdm(activities_df.iterrows(), total=activities_df.shape[0]):
        try:
            file_name = row[12].split("/")[-1]
        except (KeyError, AttributeError):
            continue

        file_path = os.path.join(activities_folder, file_name)
        file_type = file_name.split(".")[-1]
        if file_type.endswith("gz"):
            file_path, file_type = unzip_folder(file_path, file_name)

        if os.path.exists(file_path):
            stac_item = activity_to_stac(
                file_path,
                file_path,
                collection,
                row,
                file_type,
            )

            # Check if the stac_item is None and if so, print the reason
            if not stac_item:
                print(f"Skipping {file_name} due to no coordinates extracted.")
                continue

            collection.add_item(stac_item)

            generated_files_count += 1

        else:
            print(f"File {file_path} does not exist!")

    # Update Temporal and Spatial extent from all items
    collection.update_extent_from_items()

    if not Path(destination_folder).is_dir():
        Path(destination_folder).mkdir(parents=True)

    catalog.normalize_hrefs(destination_folder)
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    return generated_files_count
