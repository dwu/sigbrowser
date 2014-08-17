import sqlite3
import os
import zlib
import json
import sys
import getopt
from os import walk

class Key:
	def __init__(self):
		self.pub = {}
		self.sub = []
		self.sig = []
		self.uid = []

	def set_pub(self, line):
		self.pub = self.parse_key_line(line)

	def add_sub(self, line):
		self.sub.append(self.parse_key_line(line))

	def add_sig(self, line):
		tokens = line.split(':')

		# only add signature if not already present
		for signature in self.sig:
			if tokens[4] == signature:
				return

		self.sig.append(tokens[4])

	def add_uid(self, line):
		tokens = line.split(':')

		uid = {}
		uid['trustletter'] = tokens[1]
		uid['email'] = tokens[9][tokens[9].find("<")+1:tokens[9].find(">")]

		self.uid.append(uid)

	def __str__(self):
		return 'pub: ' + str(self.pub) + '\nsub: ' + str(self.sub) + '\nuid: ' + str(self.uid) + '\nsig: ' + str(self.sig)

	def to_json(self):
		return json.dumps({ "pub" : self.pub, "sub" : self.sub, "sig" : self.sig, "uid" : self.uid })

	def parse_key_line(self, line):
		key = {}

		tokens = line.split(':')
		key['type'] = tokens[0]
		key['trust'] = tokens[1]
		key['length'] = tokens[2]
		key['alg'] = tokens[3]
		key['id'] = tokens[4]
		key['date'] = tokens[5]
		key['email'] = tokens[9][tokens[9].find("<")+1:tokens[9].find(">")]

		return key

def create_schema(conn):
	c = conn.cursor()
	c.execute(
		'''CREATE TABLE key
		(id TEXT, key BLOB)''')
	c.execute(
		'''CREATE TABLE uid
		(pub TEXT, email TEXT, type TEXT)''')

def create_index(conn):
	c = conn.cursor()
	c.execute(
		'''CREATE INDEX key_id ON key(id)''')
	c.execute(
		'''CREATE INDEX uid_pub ON uid(pub)''')
	c.execute(
		'''CREATE INDEX uid_email ON uid(email)''')
	conn.commit()

def key_parsed(conn, key):
	c = conn.cursor()
	c.execute(
		'''INSERT INTO key
		VALUES (?, ?)''', (key.pub['id'], sqlite3.Binary(zlib.compress(key.to_json()))))

	c.execute(
		'''INSERT INTO uid
		VALUES (?, ?, ?)''', (key.pub['id'], key.pub['email'], 'pub'))

	for uid in key.uid:
		c.execute(
			'''INSERT INTO uid
			VALUES (?, ?, ?)''', (key.pub['id'], uid['email'], 'uid'))

## main
conn = sqlite3.connect('signatures.db')
create_schema(conn)

counter = 0

if len(sys.argv) < 2:
	print "usage: importer.py <folder containing sks-dump-txt-files>"
	sys.exit(1)

for (dirpath, dirnames, filenames) in walk(sys.argv[1]):
	for f in filenames:
		if f.endswith(".txt"):
			print "++ importing: " + f
			with open(dirpath + os.sep + f, 'r') as in_file:
				key = None
				for line in in_file:
					if line.startswith('pub'):
						if key != None:
							key_parsed(conn, key)
							if counter % 1000 == 0:
								conn.commit()
								# new key
								counter += 1
								key = Key()
								key.set_pub(line)
							elif line.startswith('sub'):
								key.add_sub(line)
							elif line.startswith('sig'):
								key.add_sig(line)
							elif line.startswith('uid'):
								key.add_uid(line)

create_index(conn)

conn.close()
