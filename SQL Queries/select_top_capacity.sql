select * from(
SELECT 
  ip, AVG(num_players/max_players) AS average_capacity
FROM server_data
WHERE max_players != 0
and max_players > num_players
group by ip) 
where average_capacity > 0
order by average_capacity desc
limit %s