# vkx2gpx

Convert [Vakaros](https://vakaros.com) `.vkx` sailing telemetry files to `.gpx` format.

Preserves track points (position, speed, course over ground) and start line marks (pin and committee boat) as numbered GPX waypoints.

## Installation

```bash
pip install vkx2gpx
```

Or from the repository:

```bash
pip install git+https://github.com/Matx1n3/vkx2gpx.git
```

## Usage

### CLI

```bash
vkx2gpx --input race.vkx
vkx2gpx --input race.vkx --output race.gpx
vkx2gpx --input race.vkx --verbose
```

### Python

```python
from vkx2gpx import vkx2gpx

vkx2gpx("race.vkx", "race.gpx")
```

## Output format

The generated `.gpx` file contains:

**Track points** — one per PVO record (`0x02`):
- Latitude / longitude (degrees, 1e-7 resolution)
- Elevation (meters)
- Timestamp (UTC)
- Speed over ground (m/s)

**Waypoints** — one per start line position record (`0x05`):
- Latitude / longitude
- Timestamp (UTC)
- Name: `Pin (port) 1`, `Pin (port) 2`, `Committee boat (starboard) 1`, etc.

## Acknowledgements

Based on the [Vakaros VKX format specification](https://github.com/vakaros/vkx).

## License

MIT
