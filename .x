execute(){
	export FLASK_APP=node_server.py
	flask run --port 8000 &> flask-8000.log &
	python3 run_app.py &> app-5000.log &
}
case "$1" in
	e)
		vi -p node_server.py
	;;
	"")
		execute
	;;
esac
