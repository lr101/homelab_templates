#!/bin/bash
docker exec -it stick-it-db /bin/bash -c 'pg_dump -U postgres -Fc stickitprod > /backup/dump_`date +%Y-%m-%d"_"%H_%M_%S`.dump'
