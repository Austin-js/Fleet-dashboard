import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

INPUT_FILE = Path("fleet_status.csv")
OUTPUT_FILE = Path("fleet_dashboard.html")

STATUS_COLORS = {
    "active": "#16a34a",
    "idle": "#f59e0b",
    "offline": "#6b7280",
    "low_battery": "#dc2626",
    "maintenance": "#3b82f6"
}

VALID_STATUSES = {"active", "idle", "offline", "low_battery", "maintenance"}


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_datetime(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


def time_ago(value):
    dt = parse_datetime(value)
    if not dt:
        return "Invalid timestamp"

    diff = datetime.now() - dt

    if diff.total_seconds() < 0:
        return "Future timestamp"

    minutes = int(diff.total_seconds() // 60)

    if minutes < 60:
        return f"{minutes} min ago"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"

    days = hours // 24
    return f"{days} days ago"


def load_devices():
    devices = []

    with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            lat = parse_float(row.get("lat"))
            lon = parse_float(row.get("lon"))
            battery = parse_int(row.get("battery_pct"))

            status = row["status"].strip().lower()
            if status not in VALID_STATUSES:
                continue

            # Skip rows that cannot be shown on the map
            if lat is None or lon is None:
                continue

            devices.append({
                "device_id": row.get("device_id", "").strip(),
                "name": row.get("name", "").strip(),
                "status": status,
                "battery_pct": battery,
                "lat": lat,
                "lon": lon,
                "last_seen": row.get("last_seen", "").strip(),
                "last_seen_ago": time_ago(row.get("last_seen", "").strip()),
                "location": row.get("location", "").strip(),
            })

    return devices


def generate_html(devices):
    summary = Counter(device["status"] for device in devices)

    center_lat = sum(device["lat"] for device in devices) / len(devices)
    center_lon = sum(device["lon"] for device in devices) / len(devices)

    summary_html = f"""
        <div class="summary-row active-filter" data-status="all">
            <span class="dot" style="background:#111827"></span>
            <span>All Devices</span>
            <strong>{len(devices)}</strong>
        </div>
    """

    for status in ["active", "idle", "offline", "low_battery", "maintenance"]:
        summary_html += f"""
        <div class="summary-row" data-status="{status}">
            <span class="dot" style="background:{STATUS_COLORS[status]}"></span>
            <span>{status.replace("_", " ").title()}</span>
            <strong>{summary.get(status, 0)}</strong>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Fleet Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
body {{
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}}

#map {{
    position: absolute;
    top: 0;
    bottom: 0;
    width: 100%;
}}

.side-panel {{
    position: absolute;
    top: 20px;
    right: 20px;
    width: 300px;
    background: white;
    border-radius: 12px;
    padding: 16px;
    z-index: 1000;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
}}

.side-panel h2 {{
    margin: 0 0 12px;
    font-size: 18px;
}}

.summary-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 6px 0;
    padding: 7px 8px;
    border-radius: 8px;
    cursor: pointer;
}}

.summary-row:hover,
.summary-row.active-filter {{
    background: #f3f4f6;
}}

.summary-row strong {{
    margin-left: auto;
}}

.dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
}}

.device-list {{
    margin-top: 14px;
    max-height: 300px;
    overflow-y: auto;
    border-top: 1px solid #e5e7eb;
    padding-top: 10px;
}}

.device-item {{
    padding: 9px 8px;
    border-radius: 8px;
    cursor: pointer;
    border-bottom: 1px solid #f3f4f6;
}}

.device-item:hover {{
    background: #f9fafb;
}}

.device-name {{
    font-weight: bold;
    font-size: 13px;
}}

.device-meta {{
    font-size: 12px;
    color: #6b7280;
    margin-top: 3px;
}}
</style>
</head>

<body>
<div id="map"></div>

<div class="side-panel">
    <h2>Fleet Summary</h2>
    {summary_html}
    <div class="device-list" id="device-list"></div>
</div>

<script>
var devices = {json.dumps(devices)};
var statusColors = {json.dumps(STATUS_COLORS)};
var currentStatus = "all";
var markers = [];

var map = L.map("map").setView([{center_lat}, {center_lon}], 4);

L.tileLayer("https://{{s}}.tile.openstreetmap.fr/hot/{{z}}/{{x}}/{{y}}.png", {{
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
}}).addTo(map);

function popupHtml(device) {{
    return `
        <strong>${{device.name}}</strong><br>
        Device ID: ${{device.device_id}}<br>
        Status: ${{device.status.replace("_", " ")}}<br>
        Battery: ${{device.battery_pct}}%<br>
        Location: ${{device.location}}<br>
        Last Seen: ${{device.last_seen_ago}}
    `;
}}

function createMarkers() {{
    devices.forEach(function(device) {{
        var marker = L.circleMarker([device.lat, device.lon], {{
            radius: 8,
            color: "#ffffff",
            weight: 2,
            fillColor: statusColors[device.status],
            fillOpacity: 1
        }});

        marker.bindPopup(popupHtml(device));

        marker.deviceStatus = device.status;
        marker.deviceId = device.device_id;
        marker.deviceData = device;

        marker.addTo(map);
        markers.push(marker);
    }});
}}

function applyFilter(status) {{
    markers.forEach(function(marker) {{
        map.removeLayer(marker);

        if (status === "all" || marker.deviceStatus === status) {{
            marker.addTo(map);
        }}
    }});

    map.closePopup();
}}

function renderDeviceList() {{
    var list = document.getElementById("device-list");
    list.innerHTML = "";

    var filteredDevices = devices.filter(function(device) {{
        return currentStatus === "all" || device.status === currentStatus;
    }});

    filteredDevices.forEach(function(device) {{
        var item = document.createElement("div");
        item.className = "device-item";

        item.innerHTML = `
            <div class="device-name">${{device.name}}</div>
            <div class="device-meta">
                ${{device.device_id}} · ${{device.status.replace("_", " ")}} · ${{device.battery_pct}}%
            </div>
            <div class="device-meta">${{device.location}} · ${{device.last_seen_ago}}</div>
        `;

        item.addEventListener("click", function() {{
            var selectedMarker = markers.find(function(marker) {{
                return marker.deviceId === device.device_id;
            }});

            if (selectedMarker) {{
                map.closePopup();

                map.flyTo([device.lat, device.lon], 10);
                selectedMarker.openPopup();
            }}
        }});

        list.appendChild(item);
    }});
}}

document.querySelectorAll(".summary-row").forEach(function(row) {{
    row.addEventListener("click", function() {{
        document.querySelectorAll(".summary-row").forEach(function(item) {{
            item.classList.remove("active-filter");
        }});

        row.classList.add("active-filter");
        currentStatus = row.dataset.status;

        applyFilter(currentStatus);
        renderDeviceList();
    }});
}});

createMarkers();
renderDeviceList();
</script>
</body>
</html>"""


def main():
    devices = load_devices()

    if not devices:
        raise ValueError("No valid devices found in fleet_status.csv")

    html = generate_html(devices)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"Generated {OUTPUT_FILE} with {len(devices)} mapped devices.")


if __name__ == "__main__":
    main()