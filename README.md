# Peakbagger Prepper

A command-line utility that takes a GPX file and ensures it meets the Peakbagger service requirements by resampling the track and stripping auxiliary GPX data.

## Peakbagger GPX Limitations

The Peakbagger service has limitations on the GPX files that it accepts for upload, as documented [here](https://peakbagger.com/Help/HelpGPS.aspx):

- **Max total points:** 3000 (combined track points and waypoints). Files exceeding this are resampled using the Ramer-Douglas-Peucker algorithm.
- **Max waypoints:** 150.
- **Max tracks/segments:** 50.
- **Unsupported data:** Extended data (e.g. Heart Rate, Cadence, Temperature, Power) is stripped to avoid upload issues.

## Requirements

- Python 3.13+
- `uv` (for dependency management and execution)

## Usage

You can run the script via `uv` without needing to manually activate virtual environments:

```bash
uv run peakbagger-prepper <input> <output>
```

where:
- `<input>` is either the path to an input GPX file or `-` for stdin
- `<output>` is either the path to an output GPX file or `-` for stdout

### Example

```bash
uv run peakbagger-prepper sample-files/Granites_Loop.gpx sample-files/Granites_Loop_prepped.gpx
```

## Development

To run the property-based test suite, ensure your environment is set up and execute:

```bash
uv run pytest
```
