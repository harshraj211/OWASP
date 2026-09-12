#!/bin/sh
# Block all outbound NEW connections except established return traffic
iptables -I OUTPUT -m state --state NEW -j DROP
iptables -I OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# Start the app
exec gunicorn --threads 4 -b 0.0.0.0:6024 app:app
