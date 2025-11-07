USE minecraft;
SELECT 
  DATE(timestamp) AS day,
  AVG(CASE WHEN online = true THEN 1 ELSE 0 END) AS daily_online_rate
FROM server_data
WHERE ip = %s
GROUP BY DATE(timestamp)
ORDER BY day;
