# easy history lookup

if [[ $- == *i* ]]
then
    bind '"\e[A": history-search-backward'
    bind '"\e[B": history-search-forward'
fi

##################################################################
# Docker Short Cuts   #
#                    ##         .
#              ## ## ##        ==
#           ## ## ## ## ##    ===
#       /"""""""""""""""""\___/ ===
#  ~~~ {~~ ~~~~ ~~~ ~~~~ ~~ ~ /  ===- ~~~
#       \______ o          __/
#         \    \        __/
#          \____\______/
##################################################################

dockercopy() {
  # Ask for container ID
  read -p "Enter container ID: " container_id

  # Ask for path inside the container
  read -p "Enter path inside container: " container_path

  # Ask for path on host machine
  read -p "Enter path on host machine (default: current folder): " host_path
  host_path=${host_path:-$(pwd)}

  # Copy file from container to host
  docker cp "${container_id}:${container_path}" "${host_path}"
}

dockercontainer() {
  # Check if the container ID was provided
  if [ -z "$1" ]
  then
    echo "Please provide a container ID."
    return 1
  fi

  # Get the container's name
  container_name=$(docker ps --filter "id=$1" --format "{{.Names}}")

  # Check if the container is running
  if [ -z "$container_name" ]
  then
    echo "The container with ID $1 is not running."
    return 1
  fi

  # Get into the container
  docker exec -it "$container_name" /bin/bash
}
