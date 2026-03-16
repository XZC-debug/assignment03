"""Transform raw AirNow data into CSV, JSON-L, Parquet, and GeoParquet formats."""

import pathlib
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

HOURLY_COLUMNS = [
    'valid_date',
    'valid_time',
    'aqsid',
    'site_name',
    'gmt_offset',
    'parameter_name',
    'reporting_units',
    'value',
    'data_source',
]


def _load_hourly_data(date_str):
    raw_dir = DATA_DIR / 'raw' / date_str
    date_compact = date_str.replace('-', '')
    dfs = []
    for hour in range(24):
        filepath = raw_dir / f'HourlyData_{date_compact}{hour:02d}.dat'
        if filepath.exists():
            df = pd.read_csv(
                filepath, sep='|', header=None, names=HOURLY_COLUMNS,
                encoding='latin-1', low_memory=False,
            )
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def _load_site_locations():
    raw_dirs = sorted((DATA_DIR / 'raw').iterdir())
    sites_path = None
    for d in reversed(raw_dirs):
        candidate = d / 'Monitoring_Site_Locations_V2.dat'
        if candidate.exists():
            sites_path = candidate
            break
    if sites_path is None:
        raise FileNotFoundError("No Monitoring_Site_Locations_V2.dat found in data/raw/")
    df = pd.read_csv(sites_path, sep='|', encoding='latin-1', low_memory=False)
    df = df.drop_duplicates(subset=['AQSID'], keep='first')
    return df


def prepare_hourly_csv(date_str):
    """Convert hourly data for a date to CSV.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format
    """
    df = _load_hourly_data(date_str)
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / f'{date_str}.csv', index=False)


def prepare_hourly_jsonl(date_str):
    """Convert hourly data for a date to JSON-L.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format
    """
    df = _load_hourly_data(date_str)
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_json(out_dir / f'{date_str}.jsonl', orient='records', lines=True)


def prepare_hourly_parquet(date_str):
    """Convert hourly data for a date to Parquet.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format
    """
    df = _load_hourly_data(date_str)
    out_dir = DATA_DIR / 'prepared' / 'hourly'
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_dir / f'{date_str}.parquet', index=False)


def prepare_site_locations_csv():
    """Convert site locations to CSV, deduplicated by site."""
    df = _load_site_locations()
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / 'site_locations.csv', index=False)


def prepare_site_locations_jsonl():
    """Convert site locations to JSON-L, deduplicated by site."""
    df = _load_site_locations()
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_json(out_dir / 'site_locations.jsonl', orient='records', lines=True)


def prepare_site_locations_geoparquet():
    """Convert site locations to GeoParquet with point geometries."""
    df = _load_site_locations()
    geometry = [Point(lon, lat) for lon, lat in zip(df['Longitude'], df['Latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    out_dir = DATA_DIR / 'prepared' / 'sites'
    out_dir.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(out_dir / 'site_locations.geoparquet', index=False)


if __name__ == '__main__':
    import datetime

    print('Preparing site locations...')
    prepare_site_locations_csv()
    prepare_site_locations_jsonl()
    prepare_site_locations_geoparquet()

    start_date = datetime.date(2024, 7, 1)
    end_date = datetime.date(2024, 7, 31)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        print(f'Preparing hourly data for {date_str}...')
        prepare_hourly_csv(date_str)
        prepare_hourly_jsonl(date_str)
        prepare_hourly_parquet(date_str)
        current_date += datetime.timedelta(days=1)

    print('Done.')
