#!/bin/bash

poetry export --without-hashes --format=requirements.txt | sed 's/;.*//g' > $1