#!/bin/bash

# Define the list of services
services=(
    "text_embedding_service"
    "watermark_service"
    "image_embedding_service"
    "thumbnail_service"
    "brand_info_extraction_service"
    "pinterest_api_service",
    "openai_wrapper_service",
    image_generation_service
)

# Accepts changes from the previous step
all_changes=("$@")
echo "All changes::"
echo "${all_changes[@]}"

# Check whether "restart_all_services" was modified
# If modified, include all services in the changes
for i in "${all_changes[@]}"; do
    if [[ $i == *"restart_all_services"* ]]; then
        all_changes=()
        for service in "${services[@]}"; do
            all_changes+=("$service/Dockerfile")
        done
        break
    fi
done

# Initialize parent folders array
parent_folders=()

# Process each changed file to determine the parent service folder
for i in "${all_changes[@]}"; do
    # Split the file path into components
    splits=(${i//\// })
    service_folder="${splits[0]}" # Top-level service folder
    dockerfile_location="$service_folder/Dockerfile"
    ignore_file_location="$service_folder/.cicd_ignore"
    
    # Check if the change belongs to a valid service and handle accordingly
    if [[ " ${services[*]} " == *" $service_folder "* ]]; then
        # Check if Dockerfile exists
        if [ ! -f "$dockerfile_location" ]; then
            echo "Dockerfile not found in $service_folder!"
        # Check if the service is ignored
        elif [ -f "$ignore_file_location" ]; then
            echo "Ignoring the service - $service_folder"
        else
            # Add the service folder to the parent_folders array
            parent_folders+=("$service_folder")
        fi
    fi
done

# Remove duplicates from the parent_folders array
parent_folders=($(printf "%s\n" "${parent_folders[@]}" | sort -u))
echo "Parent folders::"
echo "${parent_folders[@]}"

# Join the array into a comma-separated string
path=$(printf ",\"%s\"" "${parent_folders[@]}")
path=${path:1} # Remove the leading comma
echo "Final path::"
echo "$path"

# Update the matrix for GitHub Actions
echo "::set-output name=matrix::{\"path\": [$path] }"
