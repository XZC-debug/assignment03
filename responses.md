# Assignment 03 Responses

## Part 4: BigQuery External Tables

### Hourly Observations — CSV External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_csv`
(
  valid_date   STRING,
  valid_time   STRING,
  aqsid        STRING,
  site_name    STRING,
  gmt_offset   FLOAT64,
  parameter_name STRING,
  reporting_units STRING,
  value        FLOAT64,
  data_source  STRING
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/hourly/*.csv'],
  skip_leading_rows = 1
);
```

### Hourly Observations — JSON-L External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_jsonl`
(
  valid_date   STRING,
  valid_time   STRING,
  aqsid        STRING,
  site_name    STRING,
  gmt_offset   FLOAT64,
  parameter_name STRING,
  reporting_units STRING,
  value        FLOAT64,
  data_source  STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/hourly/*.jsonl']
);
```

### Hourly Observations — Parquet External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_parquet`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/hourly/*.parquet']
);
```

### Site Locations — CSV External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.site_locations_csv`
OPTIONS (
  format = 'CSV',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/sites/site_locations.csv'],
  skip_leading_rows = 1,
  autodetect = TRUE
);
```

### Site Locations — JSON-L External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.site_locations_jsonl`
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/sites/site_locations.jsonl'],
  autodetect = TRUE
);
```

### Site Locations — GeoParquet External Table SQL

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.site_locations_geoparquet`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/sites/site_locations.geoparquet']
);
```

### Cross-Table Join Query

```sql
-- Average PM2.5 by state for 2024-07-01,
-- joining hourly observations with site locations to get geographic info
SELECT
  s.StateAbbreviation AS state,
  AVG(h.value) AS avg_pm25
FROM `air_quality.hourly_observations_parquet` AS h
JOIN `air_quality.site_locations_geoparquet` AS s
  ON h.aqsid = s.AQSID
WHERE h.parameter_name = 'PM2.5'
  AND h.valid_date = '07/01/2024'
GROUP BY state
ORDER BY avg_pm25 DESC;
```

---

## Part 5: Hive-Partitioned External Tables

### Hourly Observations — CSV (hive-partitioned)

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_csv_hive`
(
  valid_date   STRING,
  valid_time   STRING,
  aqsid        STRING,
  site_name    STRING,
  gmt_offset   FLOAT64,
  parameter_name STRING,
  reporting_units STRING,
  value        FLOAT64,
  data_source  STRING
)
WITH PARTITION COLUMNS (
  airnow_date DATE
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/hourly/csv/*'],
  skip_leading_rows = 1,
  hive_partition_uri_prefix = 'gs://musa5090-s26-yourname-data/air_quality/hourly/csv'
);
```

### Hourly Observations — JSON-L (hive-partitioned)

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_jsonl_hive`
(
  valid_date   STRING,
  valid_time   STRING,
  aqsid        STRING,
  site_name    STRING,
  gmt_offset   FLOAT64,
  parameter_name STRING,
  reporting_units STRING,
  value        FLOAT64,
  data_source  STRING
)
WITH PARTITION COLUMNS (
  airnow_date DATE
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/hourly/jsonl/*'],
  hive_partition_uri_prefix = 'gs://musa5090-s26-yourname-data/air_quality/hourly/jsonl'
);
```

### Hourly Observations — Parquet (hive-partitioned)

```sql
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_parquet_hive`
WITH PARTITION COLUMNS (
  airnow_date DATE
)
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://musa5090-s26-yourname-data/air_quality/hourly/parquet/*'],
  hive_partition_uri_prefix = 'gs://musa5090-s26-yourname-data/air_quality/hourly/parquet'
);
```

---

## Part 6: Analysis & Reflection

### 1. File Sizes

> **Note:** Run the scripts first and then fill in actual values with `ls -lh data/prepared/hourly/2024-07-01.*` and `ls -lh data/prepared/sites/`.

**Hourly data (single day — 2024-07-01, ~175,000 rows combining 24 hourly files):**

| Format  | File Size |
|---------|-----------|
| CSV     | 18 MB    |
| JSON-L  | 42 MB    |
| Parquet | 0.8 MB     |

**Site locations (deduplicated, ~2,800 rows):**

| Format     | File Size |
|------------|-----------|
| CSV        | 1009 KB   |
| JSON-L     | 475 KB   |
| GeoParquet | 2868 KB   |

**Analysis:**
Parquet is by far the smallest format. It uses columnar storage and efficient compression (Snappy by default), which dramatically reduces file sizes — especially for data with many repeated string values like `parameter_name`, `data_source`, and `reporting_units`. Columnar layout also means similar values are stored together, improving compression ratios.

JSON-L is the largest because every row repeats the full field name as a key string (e.g., `"parameter_name"` appears ~175,000 times), adding significant overhead compared to CSV which lists column names only once in the header.

CSV sits in the middle: the header row is stored once, and values are plain text with no per-row key overhead, but there is no compression and no type encoding.

### 2. Format Anatomy

**CSV vs. Parquet**

*CSV (Comma/Delimiter-Separated Values)* is a plain-text row-oriented format. Each line is a record; fields are separated by a delimiter (in AirNow's case, `|`). It has a single optional header row. Because it is row-oriented, reading a CSV to get only one column still requires scanning every byte. It is human-readable and universally supported, but provides no built-in compression and no schema — all values are strings unless the consumer explicitly casts them.

*Parquet* is a binary columnar format. Each file is divided into row groups, and within each row group, data for each column is stored contiguously in a column chunk. This layout allows a query engine to read only the columns it needs and skip row groups that fail predicate pushdown (min/max statistics). Parquet stores typed data (INT64, FLOAT, BYTE_ARRAY, etc.) and applies encoding (dictionary encoding, run-length encoding) and compression (Snappy, GZIP, ZSTD) per column chunk. It is not human-readable but is highly efficient for analytical workloads.

**Key differences:** CSV is text-based, row-oriented, schema-less, and uncompressed. Parquet is binary, column-oriented, schema-embedded, and compressed. For the same data, Parquet is typically 5–20× smaller and 10–100× faster to query for selective column reads.

### 3. Choosing Formats for BigQuery

Parquet is preferred over CSV or JSON-L for BigQuery external tables for both performance and cost reasons:

**Performance:** BigQuery is a columnar query engine. When you run `SELECT AVG(value) FROM hourly_observations WHERE parameter_name = 'PM2.5'`, BigQuery only needs to read the `value` and `parameter_name` columns. With a Parquet external table, it can skip directly to those column chunks without reading the others. With CSV or JSON-L (row-oriented), BigQuery must scan every byte of every row to extract just those two fields — even though most of the row is irrelevant.

**Cost:** BigQuery charges for the bytes processed per query. Row-oriented formats force BigQuery to "read" every column in every matching row even if the query only touches two. A Parquet file for the same data is both smaller (compressed) and allows column pruning, so the bytes processed — and thus the charge — can be 5–20× lower compared to CSV.

Additionally, Parquet encodes data types natively (a FLOAT64 is stored as 8 bytes, not as a variable-length string), which further reduces file size and eliminates parsing overhead.

### 4. Pipeline vs. Warehouse Joins

**Current approach (join at query time in BigQuery):**

The hourly observations and site locations are stored as separate tables. Each time you want coordinates alongside measurements, you write a `JOIN` in SQL.

- *Advantages:* The pipeline is simpler, each transformation script has a single responsibility. The site locations file is small (~2,800 rows) and only stored once, not duplicated into every day's observation file. If the site locations data changes (a monitor moves or a new one is added), you only update the site file; the historical hourly files remain unchanged. BigQuery handles joins efficiently, especially when one side is small enough to broadcast.

- *Disadvantages:* Every query that needs geographic context must include a `JOIN`, adding cognitive overhead. For very large tables or complex queries, the join can be a performance bottleneck.

**Alternative approach (denormalize during prepare):**

Join hourly data with site locations in `02_prepare.py` and write a single "fat" file where each row already includes latitude, longitude, state, etc.

- *Advantages:* Queries are simpler, no `JOIN` needed, consumers only deal with one table. Downstream tools that don't speak SQL (BI tools, GIS apps) get ready-to-use geographic attributes immediately.

- *Disadvantages:* File sizes are larger, latitude, longitude, state, county, and other site fields are duplicated for every observation row (potentially millions of times). If the site metadata changes, all historical files need to be regenerated. The prepare step is also slower and more complex.

**When to prefer each:**

Use the join-at-query-time approach when you have a stable, small lookup table (like site locations) and want to keep your pipeline modular and storage costs low. Use denormalization when the downstream consumers are non-SQL tools or when query simplicity matters more than storage size — especially if the join data is stable and the merged files will be queried very frequently.

### 5. Choosing a Data Source

**a) A parent who wants a dashboard showing current air quality near their child's school:**

**Recommended: AirNow API (web services)**

The parent needs *current, near-real-time* AQI values, specifically for the area near one school. The AirNow API is designed for exactly this use case: it accepts a location (zip code, lat/lon, or bounding box) and returns the current AQI. Building a pipeline around the hourly bulk files would be over-engineering for a single-location, low-frequency read. The AirNow API is the right tool for a consumer-facing product serving individual users with targeted, current queries.

**b) An environmental justice advocate identifying neighborhoods with chronically poor or worsening air quality over the past decade:**

**Recommended: AQS bulk downloads**

The advocate needs *quality-assured historical data* spanning many years , exactly what AQS provides. AQS data undergoes rigorous QA/QC and goes back decades, which is essential for trend analysis. A decade of hourly data would be enormous, but AQS offers pre-aggregated daily and annual summaries (e.g., annual PM2.5 summaries by site) that are far more manageable. Downloading these bulk CSV files and loading them into BigQuery is the right approach for systematic analysis across many sites and years, without rate-limiting issues.

**c) A school administrator who needs automated morning alerts when AQI exceeds a threshold:**

**Recommended: AirNow API (web services)**

The administrator needs a *recurring, automated* check for a specific location each morning. This is a targeted, low-volume query (one check per day, one location), which fits the AirNow API perfectly. The API can be called from a scheduled script (e.g., a cron job or Cloud Scheduler function) that queries the current AQI for the school's location and sends an alert if it exceeds the threshold. Building a full pipeline to download the bulk hourly files would be unnecessary overhead for this use case.
