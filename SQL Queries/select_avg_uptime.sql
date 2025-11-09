USE minecraft;

SELECT AVG(CASE WHEN online = true THEN 1 ELSE 0 END)
FROM server_data
WHERE ip = %s