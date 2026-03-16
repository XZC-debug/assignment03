"""Upload prepared data files to Google Cloud Storage."""

import pathlib
from google.cloud import storage


DATA_DIR = pathlib.Path(__file__).parent.parent / 'data'

PROJECT_ID = 'cloud-to-earth'
BUCKET_NAME = 'musa5090-s26-xzc-data'


def upload_prepared_data():
    """Upload all prepared data files to GCS."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    prepared_dir = DATA_DIR / 'prepared'
    for local_path in sorted(prepared_dir.rglob('*')):
        if not local_path.is_file():
            continue
        relative = local_path.relative_to(prepared_dir)
        blob_name = f'air_quality/{relative.as_posix()}'
        blob = bucket.blob(blob_name)
        print(f'  Uploading {local_path.name} -> gs://{BUCKET_NAME}/{blob_name}')
        blob.upload_from_filename(str(local_path))


if __name__ == '__main__':
    upload_prepared_data()
    print('Done.')
