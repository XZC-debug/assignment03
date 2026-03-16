-- Part 4: Create BigQuery external tables
--
-- Create these tables in a dataset named `air_quality`.
-- Use wildcard URIs for the hourly data tables so a single table
-- spans all 31 days of files.
--
-- After creating the tables, verify they work by running:
--     SELECT count(*) FROM air_quality.<table_name>;


-- Hourly Observations — CSV
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
  uris = ['gs://musa5090-s26-xzc-data/air_quality/hourly/*.csv'],
  skip_leading_rows = 1
);


-- Hourly Observations — JSON-L
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
  uris = ['gs://musa5090-s26-xzc-data/air_quality/hourly/*.jsonl']
);


-- Hourly Observations — Parquet
CREATE OR REPLACE EXTERNAL TABLE `air_quality.hourly_observations_parquet`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://musa5090-s26-xzc-data/air_quality/hourly/*.parquet']
);


-- Site Locations — CSV
CREATE OR REPLACE EXTERNAL TABLE `air_quality.site_locations_csv`
(
  StationID       STRING,
  AQSID           STRING,
  FullAQSID       STRING,
  Parameter       STRING,
  MonitorType     STRING,
  SiteCode        STRING,
  SiteName        STRING,
  Status          STRING,
  AgencyID        STRING,
  AgencyName      STRING,
  EPARegion       STRING,
  Latitude        FLOAT64,
  Longitude       FLOAT64,
  Elevation       FLOAT64,
  GMTOffset       FLOAT64,
  CountryFIPS     STRING,
  CBSA_ID         STRING,
  CBSA_Name       STRING,
  StateAQSCode    STRING,
  StateAbbreviation STRING,
  CountyAQSCode   STRING,
  CountyName      STRING
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://musa5090-s26-xzc-data/air_quality/sites/site_locations.csv'],
  skip_leading_rows = 1
);


-- Site Locations — JSON-L
CREATE OR REPLACE EXTERNAL TABLE `air_quality.site_locations_jsonl`
(
  StationID       STRING,
  AQSID           STRING,
  FullAQSID       STRING,
  Parameter       STRING,
  MonitorType     STRING,
  SiteCode        STRING,
  SiteName        STRING,
  Status          STRING,
  AgencyID        STRING,
  AgencyName      STRING,
  EPARegion       STRING,
  Latitude        FLOAT64,
  Longitude       FLOAT64,
  Elevation       FLOAT64,
  GMTOffset       FLOAT64,
  CountryFIPS     STRING,
  CBSA_ID         STRING,
  CBSA_Name       STRING,
  StateAQSCode    STRING,
  StateAbbreviation STRING,
  CountyAQSCode   STRING,
  CountyName      STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://musa5090-s26-xzc-data/air_quality/sites/site_locations.jsonl']
);


-- Site Locations — GeoParquet
CREATE OR REPLACE EXTERNAL TABLE `air_quality.site_locations_geoparquet`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://musa5090-s26-xzc-data/air_quality/sites/site_locations.geoparquet']
);


-- Cross-table join query:
-- Average PM2.5 by state for 2024-07-01, joining hourly observations with site locations
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
