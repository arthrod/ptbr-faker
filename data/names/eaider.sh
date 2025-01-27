#!/bin/bash
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" || $key == \#* ]] && continue
    # Export each key-value pair
    export "$key=$value"
done < ~/.env/.env
