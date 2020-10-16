kill $(ps fax|grep "port 800[012]"|awk '{print $1}') &>/dev/null
kill $(ps fax|grep "run_app.py"|awk '{print $1}') &>/dev/null
kill -9 $(ps fax|grep "run_app.py"|awk '{print $1}') &>/dev/null
find . -name __pycache__ -exec rm -r {} \; &>/dev/null
rm -f *.log
