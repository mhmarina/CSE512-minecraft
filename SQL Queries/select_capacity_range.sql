USE minecraft;
SELECT 
  DATE(timestamp) AS day,
  AVG(num_players/COALESCE(NULLIF(max_players,0),1))
FROM server_data
WHERE ip = %s
GROUP BY DATE(timestamp)
ORDER BY day;