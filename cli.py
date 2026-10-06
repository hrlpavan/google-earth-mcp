#!/usr/bin/env python3
"""
Google Earth MCP CLI Utility
Command-line interface to test and operate Google Earth MCP tools directly.
"""

import sys
import os
import argparse
import json

# Import functions from server.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server

def main():
    parser = argparse.ArgumentParser(
        description="Google Earth MCP CLI - 3D Fly-To, KML Generator, Satellite Coordinates & Tours"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. fly-to
    p_fly = subparsers.add_parser("fly-to", help="Generate 3D Google Earth Web fly-to camera link")
    p_fly.add_argument("--lat", type=float, required=True, help="Latitude (-90 to 90)")
    p_fly.add_argument("--lon", type=float, required=True, help="Longitude (-180 to 180)")
    p_fly.add_argument("--alt", type=float, default=1200.0, help="Camera altitude/range in meters (default: 1200)")
    p_fly.add_argument("--heading", type=float, default=0.0, help="Azimuth heading degrees (0=N, 90=E, 180=S, 270=W)")
    p_fly.add_argument("--tilt", type=float, default=45.0, help="Camera pitch degrees (0=nadir, 45-75=3D perspective)")
    p_fly.add_argument("--title", type=str, default="", help="Location label")

    # 2. search
    p_search = subparsers.add_parser("search", help="Look up coordinates and optimal 3D camera angles")
    p_search.add_argument("query", type=str, help="Location name, strategic target, or coordinates")

    # 3. kml
    p_kml = subparsers.add_parser("kml", help="Generate KML tour file with placemarks and radar envelopes")
    p_kml.add_argument("--name", type=str, default="Mission Reconnaissance", help="Tour title")
    p_kml.add_argument("--lat", type=float, required=True, help="Center latitude")
    p_kml.add_argument("--lon", type=float, required=True, help="Center longitude")
    p_kml.add_argument("--alt", type=float, default=100.0, help="Placemark altitude in meters")
    p_kml.add_argument("--desc", type=str, default="", help="Description")
    p_kml.add_argument("--radius-km", type=float, default=25.0, help="Radar envelope radius in km")
    p_kml.add_argument("--output", type=str, default="", help="Output KML file path")

    # 4. convert
    p_conv = subparsers.add_parser("convert", help="Convert DD or DMS coordinate strings")
    p_conv.add_argument("coordinates", type=str, help="Coordinate string (e.g. '28.3922, -80.6077' or DMS)")

    args = parser.parse_args()

    if args.command == "fly-to":
        res = server.tool_google_earth_fly_to({
            "latitude": args.lat,
            "longitude": args.lon,
            "altitude_m": args.alt,
            "heading_deg": args.heading,
            "tilt_deg": args.tilt,
            "title": args.title
        })
        print(res)

    elif args.command == "search":
        res = server.tool_search_earth_location({"query": args.query})
        print(res)

    elif args.command == "kml":
        res = server.tool_create_kml_tour({
            "name": args.name,
            "description": args.desc,
            "placemarks": [
                {"name": args.name, "latitude": args.lat, "longitude": args.lon, "altitude": args.alt, "description": args.desc}
            ],
            "radar_zones": [
                {"name": f"{args.name} Perimeter", "latitude": args.lat, "longitude": args.lon, "radius_km": args.radius_km}
            ],
            "output_path": args.output or None
        })
        print(res)

    elif args.command == "convert":
        res = server.tool_convert_coordinates({"coordinates": args.coordinates})
        print(res)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
