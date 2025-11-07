USE minecraft;

SELECT ip, AVG(CASE WHEN online = true THEN 1 ELSE 0 END) AS online_rate 
FROM server_data
group by ip 
order by online_rate desc
limit %s