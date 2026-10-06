#!/usr/bin/env python3
"""
Google Earth Model Context Protocol (MCP) Server
Unified Google Earth 3D, KML/KMZ Generator, Satellite Vectoring & Camera Tours
"""

import sys
import json
import math
import os
import re
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

SERVER_NAME = "google-earth"
SERVER_VERSION = "1.0.0"

# Built-in strategic locations catalog (Space, Defense, Maritime Chokepoints, Global Metropolises)
STRATEGIC_LOCATIONS = {
    "starbase": {"name": "Starbase (SpaceX Boca Chica)", "lat": 25.9972, "lon": -97.1558, "alt": 800, "tilt": 60, "heading": 110, "desc": "SpaceX Starship orbital launch complex, Texas, USA"},
    "cape canaveral": {"name": "Cape Canaveral Space Force Station", "lat": 28.3922, "lon": -80.6077, "alt": 1500, "tilt": 55, "heading": 85, "desc": "US Space Launch Delta 45 & NASA Kennedy Space Center, Florida"},
    "kennedy space center": {"name": "NASA Kennedy Space Center LC-39A", "lat": 28.6083, "lon": -80.6043, "alt": 1000, "tilt": 55, "heading": 70, "desc": "NASA Apollo & Artemis historic launch complex 39A"},
    "vandenberg": {"name": "Vandenberg Space Force Base", "lat": 34.7420, "lon": -120.5724, "alt": 2000, "tilt": 55, "heading": 210, "desc": "USSF Western Range polar satellite launch site, California"},
    "baikonur": {"name": "Baikonur Cosmodrome Site 1/5", "lat": 45.9203, "lon": 63.3422, "alt": 1500, "tilt": 50, "heading": 45, "desc": "Gagarin's Start, historic spaceport, Kazakhstan"},
    "guiana space centre": {"name": "Guiana Space Centre (Kourou)", "lat": 5.2372, "lon": -52.7606, "alt": 1800, "tilt": 50, "heading": 30, "desc": "ESA / Arianespace equatorial spaceport, French Guiana"},
    "area 51": {"name": "Homey Airport / Groom Lake (Area 51)", "lat": 37.2431, "lon": -115.7930, "alt": 2500, "tilt": 60, "heading": 195, "desc": "USAF highly classified flight test and reconnaissance facility, Nevada"},
    "pentagon": {"name": "The Pentagon", "lat": 38.8719, "lon": -77.0563, "alt": 800, "tilt": 55, "heading": 320, "desc": "Headquarters of the US Department of Defense, Arlington, Virginia"},
    "diego garcia": {"name": "Diego Garcia Naval Support Facility", "lat": -7.3195, "lon": 72.4229, "alt": 3000, "tilt": 45, "heading": 140, "desc": "Strategic joint US/UK naval and air intelligence outpost, BIOT"},
    "pearl harbor": {"name": "Pearl Harbor Joint Base Hickam", "lat": 21.3499, "lon": -157.9497, "alt": 2500, "tilt": 50, "heading": 160, "desc": "Headquarters of US Indo-Pacific Fleet, Oahu, Hawaii"},
    "strait of hormuz": {"name": "Strait of Hormuz (Maritime Chokepoint)", "lat": 26.5667, "lon": 56.2500, "alt": 25000, "tilt": 45, "heading": 350, "desc": "Vital global oil transit chokepoint between Oman and Iran"},
    "suez canal": {"name": "Suez Canal (Great Bitter Lake)", "lat": 30.3458, "lon": 32.3578, "alt": 12000, "tilt": 40, "heading": 340, "desc": "Key international maritime transit connecting Red Sea and Mediterranean"},
    "strait of malacca": {"name": "Strait of Malacca (One Fathom Bank)", "lat": 2.8906, "lon": 101.0019, "alt": 18000, "tilt": 45, "heading": 130, "desc": "Busiest global commercial shipping lane connecting Indian and Pacific Oceans"},
    "gibraltar": {"name": "Strait of Gibraltar", "lat": 35.9620, "lon": -5.5539, "alt": 15000, "tilt": 50, "heading": 80, "desc": "Gateway between Atlantic Ocean and Mediterranean Sea"},
    "taipei": {"name": "Taipei 101", "lat": 25.0330, "lon": 121.5654, "alt": 900, "tilt": 65, "heading": 340, "desc": "Taipei, Taiwan landmark and financial center"},
    "tokyo": {"name": "Tokyo Tower / Roppongi", "lat": 35.6586, "lon": 139.7454, "alt": 900, "tilt": 65, "heading": 30, "desc": "Central Tokyo, Japan"},
    "new york": {"name": "Lower Manhattan / One World Trade", "lat": 40.7127, "lon": -74.0134, "alt": 850, "tilt": 65, "heading": 45, "desc": "New York City, USA financial district"},
    "london": {"name": "Tower Bridge & The City", "lat": 51.5055, "lon": -0.0754, "alt": 750, "tilt": 60, "heading": 290, "desc": "London, United Kingdom landmark"},
    "san francisco": {"name": "Golden Gate Bridge", "lat": 37.8199, "lon": -122.4783, "alt": 1100, "tilt": 60, "heading": 160, "desc": "San Francisco, California, USA"},
    "mount everest": {"name": "Mount Everest Summit", "lat": 27.9881, "lon": 86.9250, "alt": 9500, "tilt": 65, "heading": 190, "desc": "Earth highest mountain peak above sea level, Himalayas"}
}


def build_earth_url(lat: float, lon: float, alt: float = 1200.0, heading: float = 0.0, tilt: float = 45.0, roll: float = 0.0) -> str:
    """Generate exact 3D camera interactive Google Earth Web URL."""
    # Syntax: https://earth.google.com/web/@{lat},{lon},{ground_alt}a,{range}d,35y,{heading}h,{tilt}t,{roll}r/data=...
    range_d = max(100.0, float(alt))
    return f"https://earth.google.com/web/@{lat:.6f},{lon:.6f},0a,{range_d:.1f}d,35y,{heading:.1f}h,{tilt:.1f}t,{roll:.1f}r"


def build_maps_satellite_url(lat: float, lon: float, zoom: int = 17) -> str:
    """Generate Google Maps 3D Satellite mode URL."""
    return f"https://www.google.com/maps/@{lat:.6f},{lon:.6f},{zoom}z/data=!3m1!1e3"


def parse_dms(coord_str: str) -> Optional[float]:
    """Parse Degrees-Minutes-Seconds coordinate string into Decimal Degrees."""
    coord_str = coord_str.strip().upper()
    pattern = r'''([+-]?\d+(?:\.\d+)?)[°\s]+(?:(\d+(?:\.\d+)?)[′'\s]+)?(?:(\d+(?:\.\d+)?)[″"\s]*)?([NSEW])?'''
    match = re.search(pattern, coord_str)
    if not match:
        return None
    deg = float(match.group(1))
    minutes = float(match.group(2) or 0)
    seconds = float(match.group(3) or 0)
    direction = match.group(4)

    val = deg + (minutes / 60.0) + (seconds / 3600.0)
    if direction in ['S', 'W'] or (deg < 0 and not direction):
        val = -abs(val)
    return val


def parse_coordinates_text(text: str) -> Optional[tuple[float, float]]:
    """Parse lat/lon from arbitrary text (DD or DMS)."""
    text = text.strip()
    # Try simple comma-separated decimal pair: "37.7749, -122.4194"
    dd_match = re.search(r'([+-]?\d{1,3}(?:\.\d+)?)[,\s/]+([+-]?\d{1,3}(?:\.\d+)?)', text)
    if dd_match:
        try:
            lat = float(dd_match.group(1))
            lon = float(dd_match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except ValueError:
            pass

    # Try DMS format: 37°46'29.6"N 122°25'09.8"W
    parts = re.split(r'[,;/]|\s+(?=[+-]?\d)', text)
    if len(parts) >= 2:
        lat = parse_dms(parts[0])
        lon = parse_dms(parts[1])
        if lat is not None and lon is not None:
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon

    return None


def dd_to_dms(deg: float, is_lat: bool) -> str:
    """Format decimal degrees to standard DMS string."""
    direction = ('N' if deg >= 0 else 'S') if is_lat else ('E' if deg >= 0 else 'W')
    abs_d = abs(deg)
    d = int(abs_d)
    m = int((abs_d - d) * 60)
    s = ((abs_d - d) * 60 - m) * 60
    return f"{d}°{m:02d}'{s:04.1f}\"{direction}"


def generate_circle_coordinates(lat: float, lon: float, radius_km: float, points: int = 48) -> List[tuple[float, float]]:
    """Generate circular polygon coordinates around a center point on WGS84."""
    coords = []
    earth_radius_km = 6371.0
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    d_r = radius_km / earth_radius_km

    for i in range(points + 1):
        bearing = math.radians(i * (360.0 / points))
        target_lat = math.asin(math.sin(lat_r) * math.cos(d_r) + math.cos(lat_r) * math.sin(d_r) * math.cos(bearing))
        target_lon = lon_r + math.atan2(
            math.sin(bearing) * math.sin(d_r) * math.cos(lat_r),
            math.cos(d_r) - math.sin(lat_r) * math.sin(target_lat)
        )
        coords.append((math.degrees(target_lon), math.degrees(target_lat)))
    return coords


def create_kml_document(
    name: str,
    description: str = "",
    placemarks: Optional[List[Dict[str, Any]]] = None,
    paths: Optional[List[Dict[str, Any]]] = None,
    polygons: Optional[List[Dict[str, Any]]] = None,
    include_tour: bool = True
) -> str:
    """Generate clean, standard KML 2.2 XML with Google Earth extensions."""
    placemarks = placemarks or []
    paths = paths or []
    polygons = polygons or []

    kml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">',
        '  <Document>',
        f'    <name>{name}</name>',
        f'    <description><![CDATA[{description or "Generated by Google Earth MCP"}]]></description>',
        '    <open>1</open>',
        '',
        '    <!-- Shared Styles -->',
        '    <Style id="redPin">',
        '      <IconStyle>',
        '        <color>ff0000ff</color>',
        '        <scale>1.2</scale>',
        '        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>',
        '      </IconStyle>',
        '      <LabelStyle><scale>0.9</scale></LabelStyle>',
        '    </Style>',
        '    <Style id="bluePin">',
        '      <IconStyle>',
        '        <color>ffff0000</color>',
        '        <scale>1.1</scale>',
        '        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>',
        '      </IconStyle>',
        '    </Style>',
        '    <Style id="greenPin">',
        '      <IconStyle>',
        '        <color>ff00ff00</color>',
        '        <scale>1.1</scale>',
        '        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon>',
        '      </IconStyle>',
        '    </Style>',
        '    <Style id="tacticalPath">',
        '      <LineStyle>',
        '        <color>7f00ffff</color>',
        '        <width>3</width>',
        '      </LineStyle>',
        '      <PolyStyle><color>2000ffff</color></PolyStyle>',
        '    </Style>',
        '    <Style id="radarZone">',
        '      <LineStyle>',
        '        <color>ff00ffff</color>',
        '        <width>2</width>',
        '      </LineStyle>',
        '      <PolyStyle><color>3000ffff</color></PolyStyle>',
        '    </Style>',
        ''
    ]

    # Placemarks
    for pm in placemarks:
        p_name = pm.get("name", "Placemark")
        p_desc = pm.get("description", "")
        p_lat = pm.get("latitude", 0.0)
        p_lon = pm.get("longitude", 0.0)
        p_alt = pm.get("altitude", 0.0)
        p_style = pm.get("style", "redPin")

        kml_lines.extend([
            '    <Placemark>',
            f'      <name>{p_name}</name>',
            f'      <description><![CDATA[{p_desc}]]></description>',
            f'      <styleUrl>#{p_style}</styleUrl>',
            '      <Point>',
            '        <altitudeMode>relativeToGround</altitudeMode>',
            f'        <coordinates>{p_lon},{p_lat},{p_alt}</coordinates>',
            '      </Point>',
            '    </Placemark>'
        ])

    # Paths (LineStrings)
    for p in paths:
        p_name = p.get("name", "Flight Path")
        coords = p.get("coordinates", [])
        extrude = "1" if p.get("extrude", True) else "0"
        coord_str = " ".join([f"{c[0]},{c[1]},{c[2] if len(c) > 2 else 500}" for c in coords])

        kml_lines.extend([
            '    <Placemark>',
            f'      <name>{p_name}</name>',
            '      <styleUrl>#tacticalPath</styleUrl>',
            '      <LineString>',
            f'        <extrude>{extrude}</extrude>',
            '        <tessellate>1</tessellate>',
            '        <altitudeMode>relativeToGround</altitudeMode>',
            f'        <coordinates>{coord_str}</coordinates>',
            '      </LineString>',
            '    </Placemark>'
        ])

    # Polygons / Zones
    for poly in polygons:
        poly_name = poly.get("name", "Surveillance Zone")
        coords = poly.get("coordinates", [])
        extrude = "1" if poly.get("extrude", False) else "0"
        coord_str = " ".join([f"{c[0]},{c[1]},{c[2] if len(c) > 2 else 0}" for c in coords])

        kml_lines.extend([
            '    <Placemark>',
            f'      <name>{poly_name}</name>',
            '      <styleUrl>#radarZone</styleUrl>',
            '      <Polygon>',
            f'        <extrude>{extrude}</extrude>',
            '        <altitudeMode>relativeToGround</altitudeMode>',
            '        <outerBoundaryIs>',
            '          <LinearRing>',
            f'            <coordinates>{coord_str}</coordinates>',
            '          </LinearRing>',
            '        </outerBoundaryIs>',
            '      </Polygon>',
            '    </Placemark>'
        ])

    # Cinematic 3D Tour
    if include_tour and (placemarks or paths):
        kml_lines.extend([
            '',
            '    <!-- Automated 3D Cinematic Fly-Through Tour -->',
            '    <gx:Tour>',
            f'      <name>3D Flyover Tour - {name}</name>',
            '      <gx:Playlist>'
        ])

        tour_points = []
        for pm in placemarks:
            tour_points.append({
                "name": pm.get("name", "Target"),
                "lat": pm.get("latitude", 0.0),
                "lon": pm.get("longitude", 0.0),
                "alt": pm.get("altitude", 0.0),
                "range": 1500,
                "tilt": 60,
                "heading": 45
            })

        for p in paths:
            coords = p.get("coordinates", [])
            for pt in coords[::max(1, len(coords)//3)]:
                tour_points.append({
                    "name": p.get("name", "Waypoint"),
                    "lat": pt[1],
                    "lon": pt[0],
                    "alt": pt[2] if len(pt) > 2 else 500,
                    "range": 2500,
                    "tilt": 55,
                    "heading": 90
                })

        for idx, pt in enumerate(tour_points):
            kml_lines.extend([
                '        <gx:FlyTo>',
                '          <gx:duration>4.0</gx:duration>',
                '          <gx:flyToMode>smooth</gx:flyToMode>',
                '          <LookAt>',
                f'            <longitude>{pt["lon"]}</longitude>',
                f'            <latitude>{pt["lat"]}</latitude>',
                f'            <altitude>{pt["alt"]}</altitude>',
                f'            <heading>{pt["heading"]}</heading>',
                f'            <tilt>{pt["tilt"]}</tilt>',
                f'            <range>{pt["range"]}</range>',
                '            <altitudeMode>relativeToGround</altitudeMode>',
                '          </LookAt>',
                '        </gx:FlyTo>',
                '        <gx:Wait><gx:duration>2.0</gx:duration></gx:Wait>'
            ])

        kml_lines.extend([
            '      </gx:Playlist>',
            '    </gx:Tour>'
        ])

    kml_lines.extend([
        '  </Document>',
        '</kml>'
    ])

    return "\n".join(kml_lines)


# Tool Handlers
def tool_google_earth_fly_to(arguments: Dict[str, Any]) -> str:
    lat = float(arguments.get("latitude", 0.0))
    lon = float(arguments.get("longitude", 0.0))
    alt = float(arguments.get("altitude_m", 1200.0))
    heading = float(arguments.get("heading_deg", 0.0))
    tilt = float(arguments.get("tilt_deg", 45.0))
    roll = float(arguments.get("roll_deg", 0.0))
    title = arguments.get("title", f"Coordinates ({lat:.4f}, {lon:.4f})")

    earth_url = build_earth_url(lat, lon, alt, heading, tilt, roll)
    maps_url = build_maps_satellite_url(lat, lon)
    dms_lat = dd_to_dms(lat, True)
    dms_lon = dd_to_dms(lon, False)

    res = {
        "status": "success",
        "title": title,
        "coordinates": {
            "decimal_degrees": {"latitude": lat, "longitude": lon},
            "dms": f"{dms_lat}, {dms_lon}"
        },
        "camera_parameters": {
            "altitude_range_meters": alt,
            "heading_degrees": heading,
            "tilt_degrees": tilt,
            "roll_degrees": roll
        },
        "links": {
            "google_earth_3d_web": earth_url,
            "google_maps_satellite_3d": maps_url
        },
        "instructions": (
            f"Click or open the Google Earth 3D link to automatically fly to {title} "
            f"with cinematic {tilt}° tilt and {heading}° heading in Google Earth Web or desktop."
        )
    }
    return json.dumps(res, indent=2)


def tool_search_earth_location(arguments: Dict[str, Any]) -> str:
    query = arguments.get("query", "").strip()
    if not query:
        return json.dumps({"error": "Location query parameter is required."})

    q_lower = query.lower()

    # 1. Match local strategic dictionary
    for key, loc in STRATEGIC_LOCATIONS.items():
        if key in q_lower or q_lower in key or loc["name"].lower() in q_lower:
            earth_url = build_earth_url(loc["lat"], loc["lon"], loc["alt"], loc["heading"], loc["tilt"])
            maps_url = build_maps_satellite_url(loc["lat"], loc["lon"])
            return json.dumps({
                "status": "success",
                "match_type": "strategic_catalog",
                "name": loc["name"],
                "description": loc["desc"],
                "coordinates": {
                    "latitude": loc["lat"],
                    "longitude": loc["lon"],
                    "dms": f"{dd_to_dms(loc['lat'], True)}, {dd_to_dms(loc['lon'], False)}"
                },
                "recommended_camera": {
                    "altitude_m": loc["alt"],
                    "heading_deg": loc["heading"],
                    "tilt_deg": loc["tilt"]
                },
                "links": {
                    "google_earth_3d_web": earth_url,
                    "google_maps_satellite": maps_url
                }
            }, indent=2)

    # 2. Check if query is coordinates
    parsed = parse_coordinates_text(query)
    if parsed:
        lat, lon = parsed
        earth_url = build_earth_url(lat, lon)
        maps_url = build_maps_satellite_url(lat, lon)
        return json.dumps({
            "status": "success",
            "match_type": "parsed_coordinates",
            "name": f"Coordinate Location ({lat:.4f}, {lon:.4f})",
            "coordinates": {
                "latitude": lat,
                "longitude": lon,
                "dms": f"{dd_to_dms(lat, True)}, {dd_to_dms(lon, False)}"
            },
            "links": {
                "google_earth_3d_web": earth_url,
                "google_maps_satellite": maps_url
            }
        }, indent=2)

    # 3. Direct Google Earth Search fallback link
    search_url = f"https://earth.google.com/web/search/{urllib.parse.quote(query)}"
    maps_search = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
    return json.dumps({
        "status": "success",
        "match_type": "web_search_fallback",
        "query": query,
        "links": {
            "google_earth_search": search_url,
            "google_maps_search": maps_search
        },
        "note": "Query dispatched to Google Earth global search engine."
    }, indent=2)


def tool_create_kml_tour(arguments: Dict[str, Any]) -> str:
    name = arguments.get("name", "Google Earth Tactical Tour")
    description = arguments.get("description", "")
    placemarks = arguments.get("placemarks", [])
    paths = arguments.get("paths", [])
    polygons = arguments.get("polygons", [])
    include_tour = arguments.get("include_tour", True)
    output_path = arguments.get("output_path")

    # If circular zones are requested in simplified form
    radar_zones = arguments.get("radar_zones", [])
    for rz in radar_zones:
        r_lat = float(rz.get("latitude", 0.0))
        r_lon = float(rz.get("longitude", 0.0))
        r_km = float(rz.get("radius_km", 25.0))
        r_name = rz.get("name", f"Radar Envelope ({r_km}km)")
        circle_pts = generate_circle_coordinates(r_lat, r_lon, r_km)
        polygons.append({
            "name": r_name,
            "coordinates": circle_pts,
            "extrude": rz.get("extrude", False)
        })

    kml_content = create_kml_document(name, description, placemarks, paths, polygons, include_tour)

    # Default output path in scratch
    default_dir = "/Users/pavankumars/.gemini/antigravity/scratch/google-earth-mcp/output"
    os.makedirs(default_dir, exist_ok=True)
    if not output_path:
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name).lower()
        output_path = os.path.join(default_dir, f"{safe_name}.kml")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(kml_content)
        file_created = True
    except Exception as e:
        file_created = False
        output_path = f"Error writing file: {str(e)}"

    # Primary focus coordinates for direct Earth 3D link
    center_lat = placemarks[0].get("latitude", 0.0) if placemarks else 0.0
    center_lon = placemarks[0].get("longitude", 0.0) if placemarks else 0.0
    earth_url = build_earth_url(center_lat, center_lon, 5000.0, 45.0, 55.0) if placemarks else ""

    return json.dumps({
        "status": "success" if file_created else "warning",
        "file_path": output_path,
        "kml_size_bytes": len(kml_content),
        "total_placemarks": len(placemarks),
        "total_paths": len(paths),
        "total_polygons": len(polygons),
        "tour_included": include_tour,
        "google_earth_3d_web": earth_url,
        "instructions": (
            f"1. Open '{output_path}' directly in Google Earth Pro desktop, or import into Google Earth Web (Projects > New > Import KML).\n"
            f"2. Run the embedded 3D Flyover Tour to trigger the automated cinematic camera flyover."
        )
    }, indent=2)


def tool_convert_coordinates(arguments: Dict[str, Any]) -> str:
    coord_text = arguments.get("coordinates", "")
    parsed = parse_coordinates_text(coord_text)
    if not parsed:
        return json.dumps({"error": f"Could not parse coordinates from: '{coord_text}'. Supported formats: Decimal Degrees (e.g. 37.7749, -122.4194) or DMS (e.g. 37°46'29.6\\\"N 122°25'09.8\\\"W)"})

    lat, lon = parsed
    dms_lat = dd_to_dms(lat, True)
    dms_lon = dd_to_dms(lon, False)
    earth_url = build_earth_url(lat, lon, 1500.0, 0.0, 50.0)
    maps_url = build_maps_satellite_url(lat, lon)

    return json.dumps({
        "status": "success",
        "input": coord_text,
        "decimal_degrees": {"latitude": lat, "longitude": lon},
        "dms": f"{dms_lat}, {dms_lon}",
        "links": {
            "google_earth_3d_web": earth_url,
            "google_maps_satellite": maps_url
        }
    }, indent=2)


def tool_generate_earth_overlay(arguments: Dict[str, Any]) -> str:
    name = arguments.get("name", "Sensor Overlay")
    north = float(arguments.get("north", 0.0))
    south = float(arguments.get("south", 0.0))
    east = float(arguments.get("east", 0.0))
    west = float(arguments.get("west", 0.0))
    image_url = arguments.get("image_url", "https://maps.google.com/mapfiles/kml/shapes/radar.png")
    rotation = float(arguments.get("rotation", 0.0))

    overlay_kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Folder>
    <name>{name}</name>
    <GroundOverlay>
      <name>{name} Coverage</name>
      <Icon>
        <href>{image_url}</href>
      </Icon>
      <LatLonBox>
        <north>{north}</north>
        <south>{south}</south>
        <east>{east}</east>
        <west>{west}</west>
        <rotation>{rotation}</rotation>
      </LatLonBox>
    </GroundOverlay>
  </Folder>
</kml>'''

    center_lat = (north + south) / 2.0
    center_lon = (east + west) / 2.0
    earth_url = build_earth_url(center_lat, center_lon, 10000.0, 0.0, 45.0)

    return json.dumps({
        "status": "success",
        "name": name,
        "bounds": {"north": north, "south": south, "east": east, "west": west},
        "center_point": {"latitude": center_lat, "longitude": center_lon},
        "google_earth_3d_web": earth_url,
        "kml_snippet": overlay_kml
    }, indent=2)


# MCP Specification Tools Registry
TOOLS = [
    {
        "name": "google_earth_fly_to",
        "description": "Generate an interactive 3D Google Earth Web fly-to camera deep link with custom altitude, heading, tilt, and roll.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Target latitude (-90 to 90)."},
                "longitude": {"type": "number", "description": "Target longitude (-180 to 180)."},
                "altitude_m": {"type": "number", "description": "Camera altitude/distance in meters (default: 1200)."},
                "heading_deg": {"type": "number", "description": "Camera azimuth heading degrees: 0=North, 90=East, 180=South, 270=West (default: 0)."},
                "tilt_deg": {"type": "number", "description": "Camera pitch angle degrees: 0=Nadir/straight down, 45-75=3D Perspective (default: 45)."},
                "roll_deg": {"type": "number", "description": "Camera roll degrees (default: 0)."},
                "title": {"type": "string", "description": "Optional label or description of the location."}
            },
            "required": ["latitude", "longitude"]
        }
    },
    {
        "name": "search_earth_location",
        "description": "Look up geographic coordinates, elevation, strategic military/space/maritime data, and optimal 3D Google Earth camera parameters for locations worldwide.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name or query (e.g. 'Starbase Boca Chica', 'Cape Canaveral', 'Strait of Hormuz', 'Pearl Harbor', 'Taipei 101', or coordinates)."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_kml_tour",
        "description": "Generate standard KML/KMZ files with Placemarks, 3D extruded trajectories, circular surveillance/radar envelopes, and automated cinematic 3D flyover camera tours for Google Earth.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Title of the project or tour."},
                "description": {"type": "string", "description": "Detailed description."},
                "placemarks": {
                    "type": "array",
                    "description": "List of placemarks with name, latitude, longitude, altitude, description, style (redPin, bluePin, greenPin).",
                    "items": {"type": "object"}
                },
                "paths": {
                    "type": "array",
                    "description": "List of 3D flight paths / orbital trajectories: [{name, coordinates: [[lon, lat, alt], ...], extrude: true}].",
                    "items": {"type": "object"}
                },
                "radar_zones": {
                    "type": "array",
                    "description": "List of circular radar / surveillance envelopes: [{name, latitude, longitude, radius_km, extrude}].",
                    "items": {"type": "object"}
                },
                "include_tour": {"type": "boolean", "description": "Whether to generate an automated 3D cinematic fly-to camera tour (default: true)."},
                "output_path": {"type": "string", "description": "Optional custom file path to save the .kml file."}
            },
            "required": ["name"]
        }
    },
    {
        "name": "convert_coordinates",
        "description": "Parse and convert geographic coordinates between Decimal Degrees (DD) and Degrees-Minutes-Seconds (DMS), generating direct Google Earth 3D links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "coordinates": {"type": "string", "description": "Coordinate text in DD (e.g. '28.3922, -80.6077') or DMS (e.g. '28°23\\'31.9\\\"N 80°36\\'27.7\\\"W')."}
            },
            "required": ["coordinates"]
        }
    },
    {
        "name": "generate_earth_overlay",
        "description": "Generate a Google Earth GroundOverlay KML for tactical heatmaps, satellite tile overlays, or radar grids.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Overlay layer name."},
                "north": {"type": "number", "description": "North boundary latitude."},
                "south": {"type": "number", "description": "South boundary latitude."},
                "east": {"type": "number", "description": "East boundary longitude."},
                "west": {"type": "number", "description": "West boundary longitude."},
                "image_url": {"type": "string", "description": "URL or path of the overlay image."},
                "rotation": {"type": "number", "description": "Rotation in degrees (default: 0)."}
            },
            "required": ["name", "north", "south", "east", "west"]
        }
    }
]


def handle_rpc_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }

    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            if tool_name == "google_earth_fly_to":
                content_text = tool_google_earth_fly_to(args)
            elif tool_name == "search_earth_location":
                content_text = tool_search_earth_location(args)
            elif tool_name == "create_kml_tour":
                content_text = tool_create_kml_tour(args)
            elif tool_name == "convert_coordinates":
                content_text = tool_convert_coordinates(args)
            elif tool_name == "generate_earth_overlay":
                content_text = tool_generate_earth_overlay(args)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method/Tool '{tool_name}' not found"
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": content_text
                        }
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing {tool_name}: {str(e)}"
                        }
                    ],
                    "isError": True
                }
            }

    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not implemented"
                }
            }
        return None


def main():
    """Main stdio JSON-RPC 2.0 loop."""
    # Ensure stdout is unbuffered or flushed immediately
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
