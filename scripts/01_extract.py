"""Extract AirNow data files from EPA for a date range."""

import pathlib
import urllib.request
import datetime


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'
BASE_URL = 'https://s3-us-west-1.amazonaws.com/files.airnowtech.org/airnow'


def download_data_for_date(date_str):
    """Download AirNow data for a single date.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format (e.g., '2024-07-01')
    """
    date = datetime.date.fromisoformat(date_str)
    year = date.strftime('%Y')
    date_compact = date.strftime('%Y%m%d')

    out_dir = DATA_DIR / 'raw' / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    for hour in range(24):
        filename = f'HourlyData_{date_compact}{hour:02d}.dat'
        url = f'{BASE_URL}/{year}/{date_compact}/{filename}'
        out_path = out_dir / filename
        if not out_path.exists():
            print(f'  Downloading {filename}...')
            urllib.request.urlretrieve(url, out_path)
        else:
            print(f'  Already exists: {filename}')

    sites_filename = 'Monitoring_Site_Locations_V2.dat'
    sites_url = f'{BASE_URL}/{year}/{date_compact}/{sites_filename}'
    sites_path = out_dir / sites_filename
    if not sites_path.exists():
        print(f'  Downloading {sites_filename}...')
        urllib.request.urlretrieve(sites_url, sites_path)
    else:
        print(f'  Already exists: {sites_filename}')


if __name__ == '__main__':
    import datetime

    start_date = datetime.date(2024, 7, 1)
    end_date = datetime.date(2024, 7, 31)

    current_date = start_date
    while current_date <= end_date:
        print(f'Downloading data for {current_date}...')
        download_data_for_date(current_date.isoformat())
        current_date += datetime.timedelta(days=1)

    print('Done.')
