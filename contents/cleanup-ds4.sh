#!/bin/bash

INPUT="/dev/input/"
if ls "$INPUT" | grep -q "js1"; then
       rm /dev/input/js0
fi
