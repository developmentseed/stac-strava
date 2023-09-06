# STAC-Strava Catalog Generator 🌍🏃‍♀️

## Overview 📖

This project is designed to generate a SpatioTemporal Asset Catalog (STAC) from an archive of STAC data. It is specifically tailored to work with Strava archives.

## Requirements 🛠️

To install the required packages, run the following:

```bash
pip install -r requirements.txt
```

## Getting Started 🚀

### Obtaining Strava Archive 📦

Before running this project, you need to obtain an archive from Strava. This approach was favored over the Strava API due to the cumbersome OAuth2 procedures requiring refresh tokens.

Follow these steps to download your Strava archive:

1. Go to the [Strava website](https://www.strava.com/)
2. Navigate to 'Settings'
3. Under the 'My Account' tab, find the 'Download or Delete Your Account' section
4. Click on 'Get Started' under 'Download Request'
5. Follow the steps to download your data

Once you have downloaded the archive, unzip it and note the directory as you will need to pass it to the CLI.

### Strava Archive and STAC Metadata Mapping 🗺️

The Strava archive provides a CSV file (`activities.csv`) that contains metadata for each activity. This metadata is mapped to the STAC catalog to enrich the information available for each spatiotemporal asset.

## Usage 📝

To generate a STAC catalog, run the following command:

```bash
python src/main.py [path_to_strava_archive] [path_to_activities_directory] [path_to_collection_json] [path_to_catalog_json]
```

### Ingestion with PgSTAC

Given a [PgSTAC](https://github.com/stac-utils/pgstac) database is available and configured, you can ingest your newly generated static catalog with a few commands.

1. Generate a newline delimited JSON file of all the items:
```bash
python src/newline_items.py [path_to_catalog_json]
```

2. Load collection to PgSTAC:
```bash
pypgstac load collections ~/Documents/stac-strava/zac-strava/activities/strava/collection.json --dsn postgresql://username:password@localhost:5439/postgis --method upsert
```

3. Load items to PgSTAC:
```bash
pypgstac load items ~/Documents/stac-strava/strava_items.json --dsn postgresql://username:password@localhost:5439/postgis --method upsert
```

## Contributing 🤝

Feel free to contribute to this project by opening issues or submitting pull requests.

## License 📝

This project is licensed under the MIT License.
