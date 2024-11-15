#!/bin/bash

# Accepts changes from prev step
all_changes=("$@")
echo "all changes::"
echo $all_changes

# Check whether restart_all_services modified
# if modified, run all services
for i in ${all_changes[@]};
do
    if [[ $i == *"restart_all_services"* ]]; then
        watermark_service=watermark_service/Dockerfile
        text_embedding_service=text_embedding_service/Dockerfile
        image_embedding_service=image_embedding_service/Dockerfile
        all_changes=("${watermark_service[@]}" "${text_embedding_service[@]}" "${image_embedding_service[@]}")
        break
    fi
done

# Initialize parent folder
parent_folders=()

# find out super parents for each git changes
# and push parent_folders if there is a docker file
for i in ${all_changes[@]};
do
    splits=(${i//\// })
    service_folder=(${splits[0]}/${splits[1]})
    dockerfile_location="$service_folder/Dockerfile"
    ignore_file_location="$service_folder/.cicd_ignore"
    if [[ "${splits[0]}" == "text_embedding_service" || "${splits[0]}" == "watermark_service" || "${splits[0]}" == "image_embedding_service" ]]; then 
        if [ ! -f $dockerfile_location ]; then
            echo "Docker not found!"
        elif [ -f $ignore_file_location ]; then
            echo "Ignoring the service - $service_folder"
        else
            parent_folders+=($service_folder)
        fi
    fi
done

# Remove the duplicates
parent_folders=($(printf "%s\n" "${parent_folders[@]}" | sort -u))
echo "parent_folders::"
echo $parent_folders

# join the array
# path=$(IFS=, ; echo "\"${parent_folders[*]}\"")
path=$(printf ",\"%s\"" "${parent_folders[@]}")
path=${path:1}
echo "final path::"
echo $path

# Update matrix
echo "::set-output name=matrix::{\"path\": [ $path ] }"