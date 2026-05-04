import pytest
import gpxpy
import gpxpy.gpx
from io import StringIO
import xml.etree.ElementTree as ET
from hypothesis import given, strategies as st, settings
from peakbagger_prepper.main import process_gpx, count_points, resample_gpx, strip_extensions

def test_strip_extensions():
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    segment = gpxpy.gpx.GPXTrackSegment()
    
    point = gpxpy.gpx.GPXTrackPoint(10, 10, elevation=100)
    # Add a mock extension
    hr_ext = ET.Element("hr")
    hr_ext.text = "120"
    point.extensions.append(hr_ext)
    
    segment.points.append(point)
    track.segments.append(segment)
    gpx.tracks.append(track)
    
    # Verify extension is there initially
    assert len(gpx.tracks[0].segments[0].points[0].extensions) == 1
    
    strip_extensions(gpx)
    
    # Verify extension is removed
    assert len(gpx.tracks[0].segments[0].points[0].extensions) == 0

def test_count_points():
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    segment = gpxpy.gpx.GPXTrackSegment()
    
    for i in range(10):
        segment.points.append(gpxpy.gpx.GPXTrackPoint(i, i))
        
    track.segments.append(segment)
    gpx.tracks.append(track)
    
    for i in range(5):
        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(i, i))
        
    assert count_points(gpx) == 15

# Hypothesis strategy to generate a GPX object with a variable number of points
@st.composite
def gpx_strategy(draw):
    gpx = gpxpy.gpx.GPX()
    
    # Generate 1 to 5 tracks
    num_tracks = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_tracks):
        track = gpxpy.gpx.GPXTrack()
        # Generate 1 to 3 segments per track
        num_segments = draw(st.integers(min_value=1, max_value=3))
        for _ in range(num_segments):
            segment = gpxpy.gpx.GPXTrackSegment()
            # Generate 0 to 1000 points per segment (reduced to speed up tests)
            num_points = draw(st.integers(min_value=0, max_value=1000))
            # Just add dummy points
            segment.points = [gpxpy.gpx.GPXTrackPoint(0, 0) for _ in range(num_points)]
            track.segments.append(segment)
        gpx.tracks.append(track)
    
    # Generate some waypoints
    num_waypoints = draw(st.integers(min_value=0, max_value=50))
    gpx.waypoints = [gpxpy.gpx.GPXWaypoint(0, 0) for _ in range(num_waypoints)]
    
    return gpx

@given(gpx=gpx_strategy())
@settings(max_examples=20, deadline=None)
def test_resample_gpx_property(gpx):
    # Maximum points allowed
    MAX_POINTS = 3000
    
    original_points = count_points(gpx)
    
    resample_gpx(gpx, MAX_POINTS)
    
    new_points = count_points(gpx)
    
    # The new point count must not exceed MAX_POINTS
    assert new_points <= MAX_POINTS
    
    # If the original point count was less than or equal to MAX_POINTS,
    # it should remain unchanged.
    if original_points <= MAX_POINTS:
        assert new_points == original_points

def test_process_gpx_integration():
    input_gpx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
  <trk>
    <trkseg>
      <trkpt lat="47.6" lon="-122.3">
        <ele>100</ele>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>120</gpxtpx:hr>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="47.61" lon="-122.31">
        <ele>110</ele>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>130</gpxtpx:hr>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""
    input_stream = StringIO(input_gpx_xml)
    output_stream = StringIO()
    
    process_gpx(input_stream, output_stream)
    
    output_xml = output_stream.getvalue()
    
    # Check that it's valid XML by parsing it
    output_gpx = gpxpy.parse(output_xml)
    
    assert count_points(output_gpx) == 2
    
    # Check that extensions are stripped
    assert len(output_gpx.tracks[0].segments[0].points[0].extensions) == 0
    # Check that elevation is kept
    assert output_gpx.tracks[0].segments[0].points[0].elevation == 100.0
    
    # Check that the HR string is no longer in the XML output
    assert "gpxtpx:hr" not in output_xml
