kill $(ps fax|grep "port 800[012]"|awk '{print $1}')
kill $(ps fax|grep "run_app.py"|awk '{print $1}')
kill -9 $(ps fax|grep "run_app.py"|awk '{print $1}')
git clean -xdf
