USE minecraft;
SELECT
  EXTRACT(HOUR FROM timestamp) AS hour, 
  AVG(num_players/COALESCE(NULLIF(max_players,0),1))
FROM server_data
WHERE ip = %s AND DATE(timestamp) = %s
GROUP BY hour
ORDER BY hour;