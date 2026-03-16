"""Upload prepared hourly data to GCS with hive-partitioned folder structure."""

import pathlib
from google.cloud import storage


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

PROJECT_ID = 'cloud-to-earth'
BUCKET_NAME = 'musa5090-s26-xzc-data'


def upload_with_hive_partitioning():
    """Upload prepared hourly data with hive-partitioned folder structure."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    hourly_dir = DATA_DIR / 'prepared' / 'hourly'

    formats = [
        ('.csv',     'csv',     'data.csv'),
        ('.jsonl',   'jsonl',   'data.jsonl'),
        ('.parquet', 'parquet', 'data.parquet'),
    ]

    for ext, fmt_folder, blob_filename in formats:
        for local_path in sorted(hourly_dir.glob(f'*{ext}')):
            date_str = local_path.stem
            blob_name = f'air_quality/hourly/{fmt_folder}/airnow_date={date_str}/{blob_filename}'
            blob = bucket.blob(blob_name)
            print(f'  Uploading {local_path.name} -> gs://{BUCKET_NAME}/{blob_name}')
            blob.upload_from_filename(str(local_path))


if __name__ == '__main__':
    upload_with_hive_partitioning()
    print('Done.')
