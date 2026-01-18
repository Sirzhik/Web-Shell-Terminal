#!/bin/bash

# Load environment variables
export $(grep -v '^#' src/.env | xargs)

docker build -t wst:latest .

docker run --rm -it \       
  --env-file src/.env \
  -v "$(pwd)/src:/app/src" \
  -p 2280:2280 \
  wst:latest 

# docker run --rm -it --env-file src/.env -v "$(pwd)/src:/app/src" -p 2280:2280 wst:latest python3 main.py