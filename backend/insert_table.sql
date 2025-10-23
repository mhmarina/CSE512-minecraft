USE minecraft;

CREATE TABLE IF NOT EXISTS servers (
    ip STRING PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS server_data (
    ip STRING NOT NULL REFERENCES servers(ip) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    num_players INT,
    online BOOL,
    latency FLOAT,
    max_players INT,
    PRIMARY KEY (ip, timestamp DESC)
);