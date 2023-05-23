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

# usage: watchgit build.sh "160,170"
watchgit() {
  file_path=$1
  lines_range=$2

  checkout_commits() {
    git log --follow --reverse --pretty=format:"%H %s" -- "$file_path" | while read -r commit_id commit_message; do
      git checkout -q "$commit_id"
      # Add a small delay to allow the watch command to pick up the changes
      sleep 1
      clear
      echo "Commit ID: $commit_id"
      echo "Commit Message: $commit_message"
      echo
      display_file_changes
    done

    # Return to the original branch (e.g., main or master) after processing all commits
    git checkout main
  }

  display_file_changes() {
    sed -n "${lines_range}p" $file_path | cat -n
  }

  checkout_commits
}

# add history search ctrl - t for current folder | Requirement: `sudo apt-get install fzf`
export CUSTOM_HISTFILE="~/.bash_history_more_info" #path of the new history file
export PROMPT_COMMAND="history -a; history -c; history -r; date | xargs echo -n >>$CUSTOM_HISTFILE; echo -n ' - ' >>$CUSTOM_HISTFILE; pwd | xargs echo -n >>$CUSTOM_HISTFILE; echo -n ' - ' >>$CUSTOM_HISTFILE; tail -n 1 $HISTFILE >>$CUSTOM_HISTFILE; $PROMPT_COMMAND"

search_dir_history() {
    local selected_command=$(grep "^$(pwd) - " ~/.bash_history_more_info | awk -F" - " '{print $NF}' | fzf)
    READLINE_LINE="$selected_command"
    READLINE_POINT=${#selected_command}
}
bind -x '"\C-t": search_dir_history'

# Search ssh host using ctrl - h | Requirement: `sudo apt-get install fzf`
search_ssh_host() {
    local search_term=$(awk '/^Host/{print $2}' ~/.ssh/config | fzf --prompt "Enter hostname to search: ")
    echo "Host $search_term"
    awk "/^Host $search_term$/{flag=1;next}/^Host/{flag=0}flag" ~/.ssh/config
}
bind -x '"\C-h": search_ssh_host'

