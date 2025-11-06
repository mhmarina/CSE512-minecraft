-- handle division by 0 in backend
SELECT 
  DATE(timestamp) AS day,
  AVG(num_players/max_players) AS daily_capacity_rate
FROM server_data
WHERE ip = %s
GROUP BY DATE(timestamp)
ORDER BY day;