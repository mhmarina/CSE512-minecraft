USE minecraft;

-- Create Table if does not exist
CREATE TABLE IF NOT EXISTS servers (
    ip STRING PRIMARY KEY
);

--Insert data to servers table
INSERT INTO servers (ip)
VALUES %s
ON CONFLICT (ip) DO NOTHING;

