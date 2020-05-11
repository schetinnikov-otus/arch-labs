#!/bin/bash
tmpfile=$(mktemp /tmp/slapper.XXXXXX)
trap "{ rm -f $tmpfile; }" EXIT
echo "GET $1" > $tmpfile
f=`basename $tmpfile`
docker run -it --rm --mount type=bind,source="/tmp/",target=/targets,readonly --network=host devmtl/slapper:0.1 ./slapper  -targets /targets/$f -minY 100ms -maxY 10000ms -timeout 30s -workers 50  -rate 20
