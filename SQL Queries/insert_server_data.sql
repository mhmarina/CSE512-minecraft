USE minecraft;

-- Create Table if does not exist
CREATE TABLE IF NOT EXISTS server_data (
    ip STRING NOT NULL REFERENCES servers(ip) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    num_players INT,
    online BOOL,
    latency FLOAT,
    max_players INT,
    PRIMARY KEY (ip, timestamp DESC)
);

--Insert data to server_data table
INSERT INTO server_data (ip, timestamp, online, latency, num_players, max_players)
VALUES %s;