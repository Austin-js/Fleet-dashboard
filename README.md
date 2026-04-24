# Fleet Dashboard

This project reads a CSV file of fleet GPS devices and generates a simple, interactive HTML dashboard that can be opened directly in a browser.

---

## How to Run

1. Make sure `fleet_status.csv` is in the same directory.
2. Run the script:

```bash
python fleet_dashboard.py
```

3. Open the generated file:

```text
fleet_dashboard.html
```

---

## Features

- Interactive map with device locations
- Color-coded device statuses
- Clickable markers with device details
- Filterable summary panel
- Scrollable device list with quick navigation

---

## My Approach

### How I used AI

I used AI mainly to help me think through the task and speed up development.

First, I described my understanding of the problem to make sure I was on the right track. Then I shared my planned approach and asked for feedback and suggestions.

I used AI to help draft parts of the code, especially the HTML/JavaScript for the map and the overall structure of the script. I also explored different options for the map (like Mapbox), 
but decided to use Leaflet with OpenStreetMap-based tiles so the project wouldn’t require an API key.

After that, I reviewed and refined the output to ensure:

- The logic was correct
- Edge cases were handled properly
- The code remained clean and readable

### Colour / Status Logic

Each device status is represented with a distinct color for quick visual recognition:

- **Active** - Green (normal operation)
- **Idle** - Orange (connected but not moving)
- **Offline** - Gray (not reporting)
- **Low Battery** - Red (requires attention)
- **Maintenance** - Blue (intentionally offline)

These colors follow common UI conventions, making the dashboard intuitive for a fleet manager.

### If this were a real product

If this were a production system, I would add real-time updates using polling or WebSockets so the dashboard reflects live device changes without regenerating the HTML file.

I would also:

- Connect it to a backend and database
- Add historical tracking
- Improve filtering and search capabilities

---

## Notes

- The dashboard uses Leaflet with OpenStreetMap-based tiles via Carto.
- No API key is required.
- Internet connection is needed to load map tiles.