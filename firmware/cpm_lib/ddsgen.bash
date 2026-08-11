#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p dds_idl_cpp

# Generate IDL C++
find dds_idl/ -type f | xargs -n 1 /home/piracer/Documents/fastdds_python_ws/src/fastddsgen/scripts/fastddsgen -replace -d ./dds_idl_cpp/

# Copy headers to public inclues
mkdir -p include/cpm/dds
(cd dds_idl_cpp;find -type f) | grep \\.hpp | xargs -n 1 -I ARG cp dds_idl_cpp/ARG include/cpm/dds/
