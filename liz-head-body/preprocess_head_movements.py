#!/usr/bin/env python3
"""Clean the Roma Tre Head Movement Dataset and derive movement features.

Usage:
  python3 preprocess_head_movements.py \
    --input "/Users/lizfaulkner/Downloads/head movements dataset" \
    --output-dir "/Users/lizfaulkner/Documents/Codex/2026-11-07/hp/outputs"

The script retains every parseable sample. Duplicate timestamps are flagged and
receive blank finite-difference movement values because speed is undefined when
elapsed time is zero.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

ROW_RE = re.compile(
    r"^\s*(\d+)\s*\(\s*([-+\d.eE]+)\s*,\s*([-+\d.eE]+)\s*,\s*([-+\d.eE]+)\s*\)\s*$"
)
OUTPUT_FIELDS = [
    "session", "participant_id", "task", "recording_file", "sample_index",
    "timestamp_raw", "elapsed_seconds", "phase", "head_x", "head_y", "head_z",
    "time_delta_seconds", "velocity_x", "velocity_y", "velocity_z", "speed",
    "acceleration_x", "acceleration_y", "acceleration_z", "acceleration_magnitude",
    "quality_flag",
]
SUMMARY_FIELDS = [
    "session", "participant_id", "task", "recording_file", "samples",
    "duration_seconds", "duplicate_timestamps", "malformed_rows", "mean_sample_interval_seconds",
]


def parse_clock_timestamp(raw: str) -> float:
    """Parse HHMMSSffff as seconds since midnight; fraction digits are decimals."""
    if len(raw) < 7:
        raise ValueError(f"Timestamp has fewer than 7 digits: {raw!r}")
    hours = int(raw[:2])
    minutes = int(raw[2:4])
    seconds = int(raw[4:6])
    fraction_digits = raw[6:]
    fraction = int(fraction_digits) / (10 ** len(fraction_digits))
    if hours > 23 or minutes > 59 or seconds > 59:
        raise ValueError(f"Timestamp is outside clock range: {raw!r}")
    return hours * 3600 + minutes * 60 + seconds + fraction


def get_task(session: str, filename: str) -> str:
    if session == "Session3" and filename.endswith("-M.txt"):
        return "MA"
    return "SCWT"


def get_phase(task: str, elapsed: float) -> str:
    if task == "MA":
        return "non_stress" if elapsed < 60 else "stress"
    if elapsed < 23:
        return "non_stress_1"
    if elapsed < 43:
        return "non_stress_2"
    return "stress"


def fmt(value: float | None) -> str:
    return "" if value is None or not math.isfinite(value) else f"{value:.9g}"


def process_recording(path: Path, root: Path, writer: csv.DictWriter, summary_writer: csv.DictWriter) -> int:
    session = path.parent.parent.name
    participant_id = path.parent.name
    task = get_task(session, path.name)
    first_clock = None
    day_offset = 0.0
    previous_clock = None
    previous_elapsed = None
    previous_position = None
    previous_velocity = None
    previous_interval = None
    sample_index = 0
    malformed = 0
    duplicate_timestamps = 0
    valid_intervals = []

    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            match = ROW_RE.match(line)
            if not match:
                malformed += 1
                continue
            raw_timestamp, sx, sy, sz = match.groups()
            try:
                clock = parse_clock_timestamp(raw_timestamp)
                position = (float(sx), float(sy), float(sz))
            except (ValueError, OverflowError):
                malformed += 1
                continue

            if previous_clock is not None and clock < previous_clock - 43200:
                day_offset += 86400
            elapsed = clock + day_offset
            if first_clock is None:
                first_clock = elapsed
            elapsed -= first_clock

            dt = None if previous_elapsed is None else elapsed - previous_elapsed
            quality_flag = ""
            if dt is not None:
                if dt == 0:
                    duplicate_timestamps += 1
                    quality_flag = "duplicate_timestamp"
                elif dt < 0:
                    quality_flag = "nonmonotonic_timestamp"
                else:
                    valid_intervals.append(dt)

            velocity = None
            speed = None
            acceleration = None
            acceleration_magnitude = None
            if dt is not None and dt > 0 and previous_position is not None:
                velocity = tuple((position[i] - previous_position[i]) / dt for i in range(3))
                speed = math.sqrt(sum(v * v for v in velocity))
                if previous_velocity is not None and previous_interval is not None:
                    midpoint_dt = (dt + previous_interval) / 2
                    if midpoint_dt > 0:
                        acceleration = tuple(
                            (velocity[i] - previous_velocity[i]) / midpoint_dt for i in range(3)
                        )
                        acceleration_magnitude = math.sqrt(sum(a * a for a in acceleration))

            row = {
                "session": session,
                "participant_id": participant_id,
                "task": task,
                "recording_file": str(path.relative_to(root)),
                "sample_index": sample_index,
                "timestamp_raw": raw_timestamp,
                "elapsed_seconds": fmt(elapsed),
                "phase": get_phase(task, elapsed),
                "head_x": fmt(position[0]), "head_y": fmt(position[1]), "head_z": fmt(position[2]),
                "time_delta_seconds": fmt(dt),
                "velocity_x": fmt(None if velocity is None else velocity[0]),
                "velocity_y": fmt(None if velocity is None else velocity[1]),
                "velocity_z": fmt(None if velocity is None else velocity[2]),
                "speed": fmt(speed),
                "acceleration_x": fmt(None if acceleration is None else acceleration[0]),
                "acceleration_y": fmt(None if acceleration is None else acceleration[1]),
                "acceleration_z": fmt(None if acceleration is None else acceleration[2]),
                "acceleration_magnitude": fmt(acceleration_magnitude),
                "quality_flag": quality_flag,
            }
            writer.writerow(row)
            sample_index += 1

            previous_clock = clock
            previous_elapsed = elapsed
            previous_position = position
            previous_velocity = velocity
            previous_interval = dt if dt is not None and dt > 0 else None

    duration = 0.0 if previous_elapsed is None else previous_elapsed
    mean_interval = sum(valid_intervals) / len(valid_intervals) if valid_intervals else None
    summary_writer.writerow({
        "session": session,
        "participant_id": participant_id,
        "task": task,
        "recording_file": str(path.relative_to(root)),
        "samples": sample_index,
        "duration_seconds": fmt(duration),
        "duplicate_timestamps": duplicate_timestamps,
        "malformed_rows": malformed,
        "mean_sample_interval_seconds": fmt(mean_interval),
    })
    return sample_index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Extracted dataset folder")
    parser.add_argument("--output-dir", required=True, type=Path, help="Folder for generated CSV files")
    args = parser.parse_args()
    root = args.input.expanduser().resolve()
    out = args.output_dir.expanduser().resolve()
    recordings = sorted(root.glob("Session*/*/Record_*.txt"))
    if not recordings:
        raise SystemExit(f"No recording files found beneath {root}")
    out.mkdir(parents=True, exist_ok=True)
    data_path = out / "head_movement_cleaned.csv"
    summary_path = out / "head_movement_recording_summary.csv"
    total = 0
    with data_path.open("w", newline="", encoding="utf-8") as data_file, summary_path.open(
        "w", newline="", encoding="utf-8"
    ) as summary_file:
        writer = csv.DictWriter(data_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        summary_writer = csv.DictWriter(summary_file, fieldnames=SUMMARY_FIELDS)
        summary_writer.writeheader()
        for recording in recordings:
            total += process_recording(recording, root, writer, summary_writer)
    print(f"Processed {len(recordings)} recordings and {total:,} samples.")
    print(f"Cleaned data: {data_path}")
    print(f"Recording summary: {summary_path}")


if __name__ == "__main__":
    main()
