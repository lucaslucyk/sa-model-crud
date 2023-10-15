#!/bin/bash

poetry export --without-hashes --format=requirements.txt --only dev | sed 's/;.*//g' > $1