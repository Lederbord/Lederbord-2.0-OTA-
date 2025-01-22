#!/bin/bash

cd /usr/src/

# Define folder paths and file names
FOLDER_A="/usr/src/Partition_A"
FOLDER_B="/usr/src/Partition_B"
NEW_VERSION_FILE="$FOLDER_B/FlaskRPC"
NEW_VERSION_CHECKSUM="$FOLDER_B/FlaskRPC.sha256"
OLD_VERSION_FILE="$FOLDER_A/FlaskRPC"

# Function to check and create folders if they don't exist
check_and_create_folder() {
  local folder=$1
  if [ ! -d "$folder" ]; then
    echo "Folder '$folder' does not exist. Creating it..."
    mkdir -p "$folder"
  else
    echo "Folder '$folder' already exists."
  fi
}

# Function to verify checksum of a file
verify_checksum() {
  local file=$1
  local checksum_file=$2
  local calculated_checksum=$(sha256sum "$file" | awk '{print $1}')
  local existing_checksum=$(cat "$checksum_file" | awk '{print $1}')
  if [ $calculated_checksum = $existing_checksum ] >/dev/null 2>&1; then
    echo "Checksum verification successful for '$file'."
    return 0
  else
    echo "Checksum verification failed for '$file'."
    return 1
  fi
}

# Function to execute a file
execute_file() {
  local file=$1
  if [ -f "$file" ]; then
    chmod +x "$file"
    echo "Executing '$file'..."
    "$file"
  else
    echo "File '$file' not found. Exiting."
    exit 1
  fi
}

# Main script logic

# Step 1: Ensure the necessary folders exist
check_and_create_folder "$FOLDER_A"
check_and_create_folder "$FOLDER_B"

# Step 2: Check for the target file and its checksum in Partition_B
if [ -f "$NEW_VERSION_FILE" ] && [ -f "$NEW_VERSION_CHECKSUM" ]; then
  echo "File '$NEW_VERSION_FILE' and its checksum found in 'Partition_B'. Verifying checksum..."
  
  # Change directory to Partition_B
  cd "$FOLDER_B" || exit 1
  
  # Verify checksum
  if verify_checksum "$NEW_VERSION_FILE" "$NEW_VERSION_CHECKSUM"; then
    # If checksum passes, execute the target file
    execute_file "$NEW_VERSION_FILE"
  else
    # If checksum fails, attempt to run the fallback file from Partition_A
    echo "Checksum verification failed. Attempting to run fallback file 'FlaskRPC' from 'Partition_A'..."
    execute_file "$OLD_VERSION_FILE"
  fi
else
  echo "Either '$NEW_VERSION_FILE' or its checksum file does not exist in 'Partition_B'."
  # If no file exists in Partition_B, attempt to run the fallback file from Partition_A
  echo "Attempting to run Fallback file 'FlaskRPC' from 'Partition_A'..."
  execute_file "$OLD_VERSION_FILE"
fi

echo "Script execution completed."
