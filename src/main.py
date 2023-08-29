import os
import argparse

from stac_strava import activities_to_stac_catalog


def updated_main(
    strava_archive_path, destination_folder, collection_link, catalog_link
):
    # Define paths based on the provided Strava archive path
    csv_path = os.path.join(strava_archive_path, "activities.csv")
    activities_folder = os.path.join(strava_archive_path, "activities")

    print(activities_folder)
    # Call the function to generate the STAC catalog with collection and catalog links
    activities_to_stac_catalog(
        csv_path, activities_folder, destination_folder, collection_link, catalog_link
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Strava archive to STAC catalog"
    )
    parser.add_argument(
        "strava_archive_path", type=str, help="Path to the Strava archive directory"
    )
    parser.add_argument(
        "destination_folder",
        type=str,
        help="Destination folder to save the STAC catalog",
    )
    parser.add_argument("collection_link", type=str, help="Link to the STAC collection")
    parser.add_argument("catalog_link", type=str, help="Link to the STAC catalog root")
    args = parser.parse_args()

    updated_main(
        args.strava_archive_path,
        args.destination_folder,
        args.collection_link,
        args.catalog_link,
    )
