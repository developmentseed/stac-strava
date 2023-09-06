import os
import gzip
from xml.etree import ElementTree

from fitparse import FitFile
import fitparse


def ensure_directory_exists(directory_path):
    """Ensure that a directory exists. If not, create it."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def extract_coordinates_from_gpx(gpx_content):
    """Extracts coordinates from GPX content."""
    root = ElementTree.fromstring(gpx_content)
    namespace = {"gpx": "http://www.topografix.com/GPX/1/1"}
    coords = []
    for trkpt in root.findall(".//gpx:trkpt", namespace):
        lat = float(trkpt.attrib["lat"])
        lon = float(trkpt.attrib["lon"])
        coords.append([lon, lat])
    return coords


def extract_coordinates_from_tcx(tcx_content):
    """Extracts coordinates from TCX content."""
    # Remove any content before the XML declaration
    tcx_content = tcx_content[tcx_content.find("<?xml") :]

    try:
        root = ElementTree.fromstring(tcx_content)
    except ElementTree.ParseError:
        print("Failed to parse the TCX content. It might be malformed.")
        return []

    namespace = {"tcx": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}
    coords = []
    for trackpoint in root.findall(".//tcx:Trackpoint", namespace):
        lat_elem = trackpoint.find("tcx:Position/tcx:LatitudeDegrees", namespace)
        lon_elem = trackpoint.find("tcx:Position/tcx:LongitudeDegrees", namespace)
        if lat_elem is not None and lon_elem is not None:
            lat = float(lat_elem.text)
            lon = float(lon_elem.text)
            coords.append([lon, lat])
    return coords


def extract_coordinates_from_fit(fit_file_path):
    """Extracts coordinates from FIT file."""
    coords = []
    try:
        fitfile = FitFile(fit_file_path)
        for record in fitfile.get_messages("record"):
            lat = record.get_value("position_lat")
            lon = record.get_value("position_long")
            if lat and lon:
                coords.append([lon * (180 / 2**31), lat * (180 / 2**31)])
    except fitparse.utils.FitParseError:
        print(
            f"Failed to parse FIT file: {fit_file_path}. It might be corrupted, or no coordinates where found."
        )

    return coords


def extract_coordinates(file_path, file_type):
    """Extracts coordinates based on file type."""
    if file_type == "gpx":
        with open(file_path, "r") as file:
            content = file.read()
        return extract_coordinates_from_gpx(content)
    elif file_type == "tcx":
        with open(file_path, "r") as file:
            content = file.read()
        return extract_coordinates_from_tcx(content)
    elif file_type == "fit":
        return extract_coordinates_from_fit(file_path)
    else:
        return []


def unzip_folder(file_path, file_name):
    decompressed_path = file_path.replace(".gz", "")
    with gzip.open(file_path, "rb") as f_in, open(decompressed_path, "wb") as f_out:
        f_out.writelines(f_in)
    file_path = decompressed_path
    file_type = file_name.split(".")[-2]

    return file_path, file_type
