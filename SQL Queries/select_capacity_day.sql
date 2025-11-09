USE minecraft;

SELECT
  EXTRACT(HOUR FROM timestamp) AS hour, 
  AVG(num_players / COALESCE(NULLIF(max_players, 0), 1)) AS hourly_capacity_rate
FROM server_data
WHERE ip = %s AND DATE(timestamp) = %s
GROUP BY EXTRACT(HOUR FROM timestamp)
ORDER BY hour;