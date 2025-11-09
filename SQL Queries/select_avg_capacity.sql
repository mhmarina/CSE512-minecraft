USE minecraft;

SELECT AVG(num_players / COALESCE(NULLIF(max_players, 0), 1))
FROM server_data
where ip = %s