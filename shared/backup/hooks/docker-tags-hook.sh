#!/bin/sh
mkdir -p ./.backup
docker ps -q | while read cid; do
    cname=$(docker inspect -f '{{.Name}}' "$cid" | sed 's#^/##')
    image=$(docker inspect -f '{{.Config.Image}}' "$cid")
    digest=$(docker image inspect "$image" --format '{{index .RepoDigests 0}}' 2>/dev/null || echo "none")
    printf "%s\t%s\t%s\n" "$cname" "$image" "$digest"
done > ./.backup/docker-tags.txt