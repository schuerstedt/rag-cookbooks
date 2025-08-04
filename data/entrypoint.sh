#!/bin/bash
# Entrypoint script for marker
if [ "$1" = "marker_single" ]; then
    shift
    exec marker_single "$@"
else
    exec "$@"
fi
