USE minecraft;

INSERT INTO servers (ip)
VALUES %s
ON CONFLICT (ip) DO NOTHING;

