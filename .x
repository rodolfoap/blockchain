execute(){
	[ -d .env ] || {
		echo Installing dependencies...
		python3 -m venv .env
		python3 -m pip install -r requirements.txt
	}
	lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null || {
		export FLASK_APP=node_server.py
		echo Starting server in port 8000...
		flask run --port 8000 &> flask-8000.log &

		echo Starting application in port 5000...
		python3 run_app.py &> app-5000.log &

		echo Starting server in port 8001...; sleep 0.5
		flask run --port 8001 &> flask-8001.log &

		echo Starting server in port 8002...
		flask run --port 8002 &> flask-8002.log &

		echo Done.
	}
	multitail 	-cT ANSI flask-8000.log \
			-cT ANSI app-5000.log
#			-cT ANSI flask-8001.log \
#			-cT ANSI flask-8002.log \
}


case "$1" in
	e)
		vi -p node_server.py
	;;
	"")
		execute
	;;
esac
