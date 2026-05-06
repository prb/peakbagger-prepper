import argparse
import sys
import gpxpy
import gpxpy.gpx
from typing import TextIO

MAX_POINTS = 3000

def strip_extensions(gpx: gpxpy.gpx.GPX) -> None:
    """Removes all extensions from waypoints, routes, and tracks."""
    for waypoint in gpx.waypoints:
        waypoint.extensions = []
    
    for route in gpx.routes:
        route.extensions = []
        for point in route.points:
            point.extensions = []

    for track in gpx.tracks:
        track.extensions = []
        for segment in track.segments:
            segment.extensions = []
            for point in segment.points:
                point.extensions = []

def count_points(gpx: gpxpy.gpx.GPX) -> int:
    """Counts the total number of track points and waypoints."""
    points = len(gpx.waypoints)
    for track in gpx.tracks:
        for segment in track.segments:
            points += len(segment.points)
    return points

def resample_gpx(gpx: gpxpy.gpx.GPX, max_points: int) -> None:
    """Subsamples the GPX tracks to ensure the total number of points does not exceed max_points using Ramer-Douglas-Peucker algorithm."""
    total_points = count_points(gpx)
    if total_points <= max_points:
        return
    
    # Heuristic: the average distance between points if distributed evenly
    # provides a good order-of-magnitude guess for the RDP distance threshold.
    length_2d = gpx.length_2d()
    initial_guess = length_2d / max_points if max_points > 0 else 100.0
    
    low = 0.0
    high = max(1.0, initial_guess)  # Initial high guess in meters, will double if needed
    
    # Find an initial upper bound
    candidate = gpx.clone()
    candidate.simplify(max_distance=high)
    while count_points(candidate) > max_points:
        high *= 2.0
        candidate = gpx.clone()
        candidate.simplify(max_distance=high)

    best_gpx = candidate
    
    # Refine the distance using binary search (up to 20 iterations)
    for _ in range(20):
        mid = (low + high) / 2.0
        candidate = gpx.clone()
        candidate.simplify(max_distance=mid)
        pts = count_points(candidate)
        
        if pts <= max_points:
            best_gpx = candidate
            high = mid  # We can try to allow a smaller distance (more points)
        else:
            low = mid   # We need a larger distance (fewer points)
            
    # Apply the best result
    if best_gpx:
        gpx.tracks = best_gpx.tracks
        gpx.routes = best_gpx.routes

def process_gpx(input_stream: TextIO, output_stream: TextIO) -> None:
    gpx = gpxpy.parse(input_stream)
    
    strip_extensions(gpx)
    resample_gpx(gpx, MAX_POINTS)
    
    output_stream.write(gpx.to_xml())

def main() -> None:
    parser = argparse.ArgumentParser(description="Prepares GPX files for Peakbagger by resampling and stripping unsupported extensions.")
    parser.add_argument("input", help="Path to input GPX file, or '-' for stdin")
    parser.add_argument("output", help="Path to output GPX file, or '-' for stdout")
    
    args = parser.parse_args()
    
    if args.input == '-':
        input_stream = sys.stdin
    else:
        input_stream = open(args.input, 'r', encoding='utf-8')
        
    try:
        if args.output == '-':
            output_stream = sys.stdout
        else:
            output_stream = open(args.output, 'w', encoding='utf-8')
            
        try:
            process_gpx(input_stream, output_stream)
        finally:
            if args.output != '-':
                output_stream.close()
    finally:
        if args.input != '-':
            input_stream.close()

if __name__ == "__main__":
    main()
