SELECT
    first_dimensions.name AS dimension_name,
    DATE_TRUNC('hour', events.recorded_date) AS current_hour,
    COUNT(*) AS num_events
FROM events
INNER JOIN
    first_dimensions
    ON first_dimensions.id = events.first_dimension_id
GROUP BY first_dimensions.name, current_hour
ORDER BY first_dimensions.name, current_hour;
