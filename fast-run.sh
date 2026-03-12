#!/bin/bash

docker build -t wst:latest .
docker run -v db:/app/src/database -p 2280:2280 wst:latest
