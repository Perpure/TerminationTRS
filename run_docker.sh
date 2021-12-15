#!/bin/bash

docker build -t refal:tests .
docker run --rm -v/home/fall/TerminationTRS:/out --name tests refal:tests 
docker rm tests
