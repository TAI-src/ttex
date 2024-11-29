#!/bin/bash
# First argument is assumed to be the mode (listener, job)
# Second argument is assumed to be the command to start

helpFunction()
{
   echo ""
   echo "Usage: $0 -l / -j"
   echo -e "\t-l Starts listener and assumes the following env variables "
   echo -e "\t DOCKER_USER_NAME; DOCKER_PWD, WANDB_Q; WANDB_ENTITY; WANDB_API_KEY"
   echo -e "\t-j Starts job and assumes the following env variables"
   echo -e "\t ENTRY_PATH WANDB_API_KEY"
   exit 1 # Exit script after printing help
}

while getopts "lj" opt
do
   case "$opt" in
      l ) listener="True" ;;
      j ) job="True" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# only allow one mode
if [ -n "$listener" ] && [ -n "$job" ]
then
   echo "Only one mode allowed at a time";
   helpFunction
fi

# if listener is requested to start
if [ -n "$listener" ]
then
    if [ -z "$DOCKER_PWD" ] || [ -z "$DOCKER_USER_NAME" ] || [ -z "$WANDB_ENTITY" ] || [ -z "$WANDB_Q" ] || [ -z "$WANDB_API_KEY" ]
    then
        echo "Missing env variable for listener mode";
        helpFunction
    fi
    # Log into docker as the jobs are started from within this container
    echo $DOCKER_PWD | docker login --username $DOCKER_USER_NAME --password-stdin
    # Start the listener agent
    wandb launch-agent -e $WANDB_ENTITY -q $WANDB_Q
fi

# if job is requested to start
if [ -n "$job" ]
then
    if [ -z "$ENTRY_PATH" ] || [ -z "$WANDB_API_KEY" ]
    then
        echo "Missing env variable for job mode";
        helpFunction
    fi
    eval "python $ENTRY_PATH"
fi
