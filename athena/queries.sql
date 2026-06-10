-- ============================================================
-- IoT Sensor Pipeline -- Analytics Queries
-- Database: iot_sensor_db | Table: processed
-- Author: Karthik John Babu
-- ============================================================

-- QUERY 1: Average temperature per machine
-- Business question: Which machines are running hottest?
SELECT
    machine_id,
    ROUND(AVG(temperature_c), 2) AS avg_temp,
    ROUND(MAX(temperature_c), 2) AS max_temp,
    ROUND(MIN(temperature_c), 2) AS min_temp,
    COUNT(*) AS reading_count
FROM "iot_sensor_db"."processed"
GROUP BY machine_id
ORDER BY avg_temp DESC
LIMIT 20;

-- QUERY 2: Machines with temperature above 85C
-- Business question: Which machines need immediate attention?
SELECT
    machine_id,
    timestamp,
    ROUND(temperature_c, 2) AS temperature_c,
    temp_category,
    ROUND(vibration_hz, 2) AS vibration_hz,
    status
FROM "iot_sensor_db"."processed"
WHERE temperature_c > 85
ORDER BY temperature_c DESC;

-- QUERY 3: Anomaly detection using Z-score
-- Business question: Which machines show statistically unusual behaviour?
-- Z-score > 2 means more than 2 standard deviations above normal
WITH machine_stats AS (
    SELECT
        machine_id,
        AVG(temperature_c) AS mean_temp,
        STDDEV(temperature_c) AS stddev_temp
    FROM "iot_sensor_db"."processed"
    GROUP BY machine_id
),
recent_readings AS (
    SELECT
        machine_id,
        AVG(temperature_c) AS recent_avg
    FROM "iot_sensor_db"."processed"
    GROUP BY machine_id
)
SELECT
    r.machine_id,
    ROUND(r.recent_avg, 2) AS avg_temp,
    ROUND(s.mean_temp, 2) AS overall_mean,
    ROUND(s.stddev_temp, 2) AS stddev,
    ROUND((r.recent_avg - s.mean_temp) / NULLIF(s.stddev_temp, 0), 2) AS z_score
FROM recent_readings r
JOIN machine_stats s ON r.machine_id = s.machine_id
WHERE ABS((r.recent_avg - s.mean_temp) / NULLIF(s.stddev_temp, 0)) > 0.5
ORDER BY z_score DESC;

-- QUERY 4: Temperature category distribution
-- Business question: What percentage of readings were CRITICAL vs NORMAL?
SELECT
    temp_category,
    COUNT(*) AS reading_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM "iot_sensor_db"."processed"
GROUP BY temp_category
ORDER BY reading_count DESC;

-- QUERY 5: Machine-01 readings over time
-- Business question: Show the full timeline for the machine with anomalies
SELECT
    timestamp,
    ROUND(temperature_c, 2) AS temperature_c,
    temp_category,
    ROUND(vibration_hz, 2) AS vibration_hz,
    ROUND(pressure_bar, 2) AS pressure_bar,
    status
FROM "iot_sensor_db"."processed"
WHERE machine_id = 'Machine-01'
ORDER BY timestamp DESC
LIMIT 20;

