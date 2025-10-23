USE minecraft;

-- insert all in batch
INSERT INTO servers (ip)
VALUES %s
ON CONFLICT (ip) DO NOTHING;

INSERT INTO server_data (ip, timestamp, online, latency, num_players, max_players)
VALUES %s;