USE minecraft;

INSERT INTO server_data (ip, timestamp, online, latency, num_players, max_players)
VALUES (%s, %s, %s, %s, %s, %s);