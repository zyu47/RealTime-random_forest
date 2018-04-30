#!/usr/bin/env bash

ENV_NAME="env"

if [ -e ../$ENV_NAME ]
then
    echo "Existing environment with same name ($ENV_NAME) found. Do you want to delete it first?"
    read
    if [ $REPLY == 'y' ]
    then
	rm -rf "../$ENV_NAME"
	virtualenv -p python "../$ENV_NAME"
    fi
else
    echo "Installing into the existing environment: $ENV_NAME"
fi
	
source "../$ENV_NAME/bin/activate"

# Install tensorflow 0.10
pip install --upgrade tensorflow-gpu || exit 1

# Setup OpenCV
ln -s "~vision/usr/rahul/local/lib/python2.7/site-packages/cv2.so" ../env/lib/python2.7/site-packages/cv2.so || exit 1

# Install matplotlib
pip install --upgrade matplotlib || exit 1

echo "Please copy these lines into your .bashrc"
echo -e "replacing paths as necessary:\n\n"
cat ./setup-env.sh || exit 1
echo -e "\n\nPress any key when done"
read -s -n 1
echo "Done"
