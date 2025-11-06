-- date should look like this: '2025-11-05' 
SELECT
  DATE(timestamp) AS day,
  EXTRACT(HOUR FROM timestamp) AS hour, 
  case when online = true then 1 else 0 END
FROM server_data
WHERE ip = %s AND DATE(timestamp) = %s
ORDER BY hour;