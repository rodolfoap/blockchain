execute(){
	export FLASK_APP=node_server.py
	lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null || {
		flask run --port 8000 &> flask-8000.log &
		python3 run_app.py &> app-5000.log &
		sleep 0.5
		flask run --port 8001 &> flask-8001.log &
		flask run --port 8002 &> flask-8002.log &
	}
	multitail 	-cT ANSI flask-8000.log \
			-cT ANSI flask-8001.log \
			-cT ANSI flask-8002.log \
			-cT ANSI app-5000.log
}
case "$1" in
	e)
		vi -p node_server.py
	;;
	"")
		execute
	;;
esac
