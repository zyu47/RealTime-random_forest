echo 'logging into maserati for Depth RH'
gnome-terminal -x bash -c "ssh -t maserati 'cd $PWD/../handRecognition/; source ../env/bin/activate; python depth_client.py RH;bash;'" &
sleep 1

echo 'logging into magenta for Depth LH'
gnome-terminal -x bash -c "ssh -t magenta 'cd $PWD/../handRecognition/; source ../env/bin/activate; python depth_client.py LH;bash;'" &
sleep 1

echo 'logging into yellow for Depth Head'
gnome-terminal -x bash -c "ssh -t lotus 'cd $PWD/../headRecognition/; source ../env/bin/activate; python head_client.py;bash;'" &
sleep 1

echo 'logging into cyan for skeleton recogntion'
gnome-terminal -x bash -c "ssh -t cyan 'cd $PWD/../skeletonRecognition/; python apart-together.py;bash;'" &
