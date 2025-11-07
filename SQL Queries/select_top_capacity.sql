USE minecraft;

SELECT * from(
SELECT 
  ip, AVG(num_players/max_players) AS average_capacity
FROM server_data
WHERE max_players != 0
AND max_players > num_players
GROUP BY ip) 
WHERE average_capacity > 0
ORDER BY average_capacity DESC
LIMIT %s