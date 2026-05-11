import struct
import gpxpy
import gpxpy.gpx
from datetime import datetime, timezone

PAYLOAD_SIZES = {
    0xFF: 7,   # Page Header
    0xFE: 2,   # Page Terminator
    0x01: 32,  # Internal
    0x02: 44,  # PVO (main)
    0x03: 20,  # Declination
    0x04: 13,  # Race Timer
    0x05: 17,  # Line Position
    0x06: 18,  # Shift Angle
    0x07: 12,  # Internal
    0x08: 13,  # Device Config
    0x0A: 16,  # Wind
    0x0B: 16,  # Speed Through Water
    0x0C: 12,  # Depth
    0x0E: 16,  # Internal
    0x0F: 16,  # Load
    0x10: 12,  # Temperature
    0x20: 13,  # Internal
    0x21: 52,  # Internal
}

LINE_END_TYPES = {
    0: 'Pin (port)',
    1: 'Committee boat (starboard)',
}

def parse_vkx(filepath):
    points = []
    marks  = []

    with open(filepath, 'rb') as f:
        data = f.read()

    i = 0
    while i < len(data):
        key = data[i]
        i += 1

        payload_size = PAYLOAD_SIZES.get(key)
        if payload_size is None:
            i += 1  # unknown key, advance one byte and resync
            continue

        if i + payload_size > len(data):
            break

        payload = data[i:i + payload_size]
        i += payload_size

        if key == 0x02:  # Position, Velocity, Orientation
            ts_ms   = struct.unpack_from('<Q', payload, 0)[0]
            lat_raw = struct.unpack_from('<i', payload, 8)[0]
            lon_raw = struct.unpack_from('<i', payload, 12)[0]
            sog     = struct.unpack_from('<f', payload, 16)[0]  # m/s
            cog     = struct.unpack_from('<f', payload, 20)[0]  # radians
            alt     = struct.unpack_from('<f', payload, 24)[0]  # meters

            lat = lat_raw * 1e-7
            lon = lon_raw * 1e-7
            ts  = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)

            points.append({
                'time':    ts,
                'lat':     lat,
                'lon':     lon,
                'alt':     alt,
                'sog_ms':  sog,
                'cog_rad': cog,
            })

        elif key == 0x05:  # Line Position (buoys/marks)
            ts_ms    = struct.unpack_from('<Q', payload, 0)[0]
            end_type = struct.unpack_from('<B', payload, 8)[0]
            lat      = struct.unpack_from('<f', payload, 9)[0]
            lon      = struct.unpack_from('<f', payload, 13)[0]
            ts       = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
            label    = LINE_END_TYPES.get(end_type, f'Unknown mark ({end_type})')

            marks.append({
                'time':  ts,
                'lat':   lat,
                'lon':   lon,
                'label': label,
            })

    return points, marks


def vkx2gpx(vkx_path, gpx_path, verbose=False):
    points, marks = parse_vkx(vkx_path)

    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    # Telemetry track
    for p in points:
        pt = gpxpy.gpx.GPXTrackPoint(
            latitude=p['lat'],
            longitude=p['lon'],
            elevation=p['alt'],
            time=p['time']
        )
        pt.speed = p['sog_ms']
        segment.points.append(pt)

    # Waypoints for each buoy/mark
    counters = {}
    waypoint_names = []
    for m in marks:
        counters[m['label']] = counters.get(m['label'], 0) + 1
        name = f"{m['label']} {counters[m['label']]}"
        waypoint_names.append(name)
        wp = gpxpy.gpx.GPXWaypoint(
            latitude=m['lat'],
            longitude=m['lon'],
            name=name,
            time=m['time'],
        )
        gpx.waypoints.append(wp)

    with open(gpx_path, 'w') as f:
        f.write(gpx.to_xml())

    if verbose:
        print(f"Exported {len(points)} points and {len(marks)} marks to {gpx_path}")
        for m, name in zip(marks, waypoint_names):
            print(f"  {name}: ({m['lat']:.6f}, {m['lon']:.6f}) @ {m['time']}")
