import sqlite3
import json
import zlib
from bottle import route, run, template, static_file, request, response

@route('/')
@route('/index.html')
def index():
	return static_file('index.html', root='./static')


@route('/static/<filepath:path>')
def serve_static(filepath):
	return static_file(filepath, root='./static')

@route('/key')
def query_key():
	response.headers['Content-Type'] = 'application/json'

	result = []
	c = conn.cursor()
	for row in c.execute('SELECT pub, email, type FROM uid WHERE email LIKE ?', (request.query.email, )):
		result.append({ "id" : row[0], "email": row[1], "type": row[2] })

	return json.dumps({ "keys" : result })

@route('/key/<id>')
def get_key(id):
	key = None

	response.headers['Content-Type'] = 'application/json;charset=UTF-8'

	c = conn.cursor()
	for row in c.execute('SELECT key FROM key WHERE id = ?', (id.upper(), )):
		key = json.loads(zlib.decompress(row[0]))

	return key

## main
conn = sqlite3.connect("signatures.db")
run(host='localhost', port=8080, server="tornado")
