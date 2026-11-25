# Head movement preprocessing

Processed from the extracted Roma Tre Head Movement Dataset. Supply your own dataset path when rerunning the preprocessing script.

## Outputs

- `head_movement_cleaned.csv`: one row per recorded sample, with head position, elapsed time, task phase, and finite-difference movement features.
- `head_movement_recording_summary.csv`: one row per recording, with sample counts, duration, mean sample interval, and data-quality counts.
- `preprocess_head_movements.py`: reproducible Python script used to create the CSVs.

## Processing choices

- Parsed each timestamp as `HHMMSSffff`, then converted it to elapsed seconds from the start of its recording.
- Kept original rows and position coordinates; did not interpolate, smooth, or drop samples.
- Computed velocity from the position change divided by the actual interval between timestamps. Computed acceleration from changes in velocity using the interval between sample midpoints. Values are finite-difference estimates and may be noisy.
- Kept 255 duplicate-timestamp samples and marked them `duplicate_timestamp`. Speed and acceleration are blank where a zero or unavailable time interval makes the derivative undefined.
- No malformed recording rows were found.
- Assigned phase from elapsed recording time: SCWT uses `non_stress_1` before 23 s, `non_stress_2` from 23 to under 43 s, then `stress`; MA uses `non_stress` before 60 s, then `stress`.
- Dataset coordinate units are preserved as recorded; no unit conversion was applied.
- Questionnaire CSVs were not merged into the frame-level movement data.

## Columns

- `session`, `participant_id`, `task`, `recording_file`: recording identifiers.
- `sample_index`, `timestamp_raw`, `elapsed_seconds`: original row order and time fields.
- `phase`: phase label based on the documented task timing.
- `head_x`, `head_y`, `head_z`: recorded head position.
- `time_delta_seconds`: actual time since the preceding sample.
- `velocity_x`, `velocity_y`, `velocity_z`, `speed`: coordinate-wise velocity and its magnitude.
- `acceleration_x`, `acceleration_y`, `acceleration_z`, `acceleration_magnitude`: finite-difference acceleration and its magnitude.
- `quality_flag`: blank unless the sample has a duplicate or nonmonotonic timestamp.

This is a movement-only preprocessing output. It does not include EgoBody body-pose data or infer stress beyond assigning the dataset's task-phase labels.
