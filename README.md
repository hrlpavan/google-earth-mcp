# Google Earth Model Context Protocol (MCP) Server

A high-performance Model Context Protocol (MCP) server providing 3D Google Earth Web fly-to camera links, dynamic KML/KMZ tour generation, coordinate conversion, and satellite target vectoring. Zero external API keys required.

---

## 🚀 Capabilities

1. **`google_earth_fly_to`**
   - Computes exact 3D camera vector parameters (`latitude`, `longitude`, `altitude_m`, `heading_deg`, `tilt_deg`, `roll_deg`).
   - Generates interactive 3D Google Earth Web deep links (`https://earth.google.com/web/@...`) and Google Maps 3D satellite links.

2. **`create_kml_tour`**
   - Generates complete OpenGIS KML 2.2 documents with Google Earth extensions (`gx:Tour`, `gx:FlyTo`, `gx:duration`, `gx:Wait`).
   - Supports 3D Placemarks with custom pins, extruded 3D flight paths / orbital trajectories, and circular surveillance / radar envelopes.
   - Automatically saves to disk and provides one-click desktop or web import instructions.

3. **`search_earth_location`**
   - Instant resolution of strategic defense installations, spaceports, maritime transit chokepoints, landmarks, and global cities.
   - Computes optimal 3D camera angles and elevations for each target.

4. **`convert_coordinates`**
   - Bi-directional conversion between Decimal Degrees (DD) and Degrees Minutes Seconds (DMS).
   - Instant generation of Google Earth 3D telemetry links.

5. **`generate_earth_overlay`**
   - Generates KML `<GroundOverlay>` specifications for tactical heatmaps, sensor coverage fans, and custom satellite imagery tiles.

---

## ⚙️ Antigravity MCP Configuration

The server is globally registered in `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "google-earth": {
      "command": "python3",
      "args": [
        "/Users/pavankumars/.gemini/antigravity/scratch/google-earth-mcp/server.py"
      ]
    }
  }
}
```

---

## 🛠️ CLI Usage

You can also run tools directly from the command line:

```bash
# 1. 3D Fly-To Camera link
python3 cli.py fly-to --lat 25.9972 --lon -97.1558 --alt 800 --tilt 60 --heading 110 --title "Starbase Boca Chica"

# 2. Search Strategic Target
python3 cli.py search "Baikonur"

# 3. Generate KML 3D Tour with 40km Radar Envelope
python3 cli.py kml --name "Space Force Ops" --lat 28.3922 --lon -80.6077 --radius-km 40

# 4. Coordinate Conversion (DMS to DD + Earth 3D link)
python3 cli.py convert "37°46'29.6\"N 122°25'09.8\"W"
```

---

## 📂 Architecture

- `server.py`: Pure standard-library Python JSON-RPC 2.0 stdio MCP server (< 5ms startup, zero external dependencies).
- `cli.py`: Terminal test and operational harness.
- `output/`: Directory where generated `.kml` and `.kmz` files are stored.
