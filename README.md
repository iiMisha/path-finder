# path-finder

Find shortest paths on map with control points.

Designed to solve choosing parts of [Московский Марш-Бросок (ММБ)](http://mmb.progressor.ru/).

## Requirements

- python3 only.

- ```pip install -r requirements.txt```

- Install tesseract ([guide](https://github.com/tesseract-ocr/tesseract/wiki))

- Tested on Windows and Mac OS.

## Usage

```python orcestrate.py <map_filename>```

## Execution steps

Works in 3 steps:

1. Automatically find control points on map using Circle Hough Transform. Then find CP's names using `tesseract` (prepare_map.py)
2. Show map to user to fix mistakes and specify scale (check_for_mistakes.py)
3. Find best routes and save outputs (top_routes.py)

## Fixing step

1. You need to check that all CP found (green circle added) and CP's names are correct (black text in green circle).
You can change name and penalty of CP by left click in CP. Also you can add new CP by left click in free space.

2. You need to find 2 points on map, distance between witch is 1 km, and right click them.
