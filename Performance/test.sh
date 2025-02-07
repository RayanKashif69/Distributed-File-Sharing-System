#!/bin/bash

trap "kill 0" EXIT  # Ensure all subprocesses are killed when the script exits

NUM_CLIENTS=5
DOWNLOADS_PER_CLIENT=100
SERVER_HOST="localhost"
USERNAME="test_user"

# Get a valid file from the server directory
FILE_LIST=($(ls /server_files))
if [ ${#FILE_LIST[@]} -eq 0 ]; then
    echo " No files available on the server!"
    exit 1
fi

RANDOM_FILE="${FILE_LIST[$RANDOM % ${#FILE_LIST[@]}]}"  # Select a random file
echo "📂 Selected file for download: '$RANDOM_FILE'"

# Ensure controlled execution
for i in $(seq 1 $NUM_CLIENTS)
do
   echo " Starting Client $i"
   (
      for j in $(seq 1 $DOWNLOADS_PER_CLIENT)
      do
         echo "   Client $i downloading file ($j / $DOWNLOADS_PER_CLIENT)"
         python3 clientpart2.py "$USERNAME" "$SERVER_HOST" "GET $RANDOM_FILE"
      done
      echo " Client $i finished downloads."
   ) &
done

wait  # Wait for all processes to complete
echo " Load test completed!"
