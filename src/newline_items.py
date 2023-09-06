import json
import argparse

import pystac


parser = argparse.ArgumentParser(description='Process a STAC catalog.')
parser.add_argument('catalog_file', type=str, help='Path to the STAC catalog JSON file')

args = parser.parse_args()

catalog_file = args.catalog_file

print(f"Connecting to static catalog from {catalog_file}...")
catalog = pystac.Catalog.from_file(catalog_file)

collections = list(catalog.get_collections())
if len(collections) != 1:
    raise ValueError(
        "Expected catalog to contain a single collection of Strava activities."
    )


print("Creating newline delimited JSON file of items...")
collection = collections[0]
with open(f"{collection.id}_items.json", "w") as f:
    for item in collection.get_all_items():
        item_dict = item.make_asset_hrefs_absolute().to_dict()
        item_str = json.dumps(item_dict)
        f.write(item_str + "\n")
