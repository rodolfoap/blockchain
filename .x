execute(){
	export FLASK_APP=node_server.py
	flask run --port 8000 &> flask-8000.log &
	python3 run_app.py &> app-5000.log &
	sleep 0.5
	flask run --port 8001 &> flask-8001.log &
	flask run --port 8002 &> flask-8002.log &
	multitail flask-8000.log flask-8001.log flask-8002.log app-5000.log
}
case "$1" in
	e)
		vi -p node_server.py
	;;
	"")
		execute
	;;
esac
