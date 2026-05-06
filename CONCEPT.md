This project is intended to provide a commandline utility that will take a GPX file and ensure that it meets the Peakbagger service requirements, e.g., by resampling the track to a maximum of 3000 points or stripping auxilliary GPX data like HR, Cadence, and Temperature data that Peakbagger does not support.

## Peakbagger GPX Limitations
The Peakbagger service has limitations on the GPX files that it accepts for upload, as documented here: https://peakbagger.com/Help/HelpGPS.aspx

- **Max total points:** 3000 (combined track points and waypoints). Files exceeding this must be resampled.
- **Max waypoints:** 150.
- **Max tracks/segments:** 50.
- **Unsupported data:** Extended data (e.g. Heart Rate, Cadence, Temperature, Power) should be stripped to avoid upload issues. Peakbagger also ignores/strips elevation and timestamp data, though standard GPX elements are typically harmless.

## Intended Usage
Intended usage would be:

```
uv run peakbagger-prepper input output
```

where

- `input` is either the path to an input GPX file or `-` for stdin
- `output` is either the path to an output GPX file or `-` for stdout

The tool should be written in Python 3 subject to the expectations documented in the Python coding standards for the project.