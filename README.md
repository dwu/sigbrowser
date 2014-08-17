# PGP Signature Browser

## About

*PGP Signature Browser* allows visualizing the Web of Trust and navigate
signature relationships between keys interactively using
[vis.js](http://visjs.org) and
[bottle.py](http://bottlepy.org/docs/dev/index.html).

![Screenshot](/doc/sigbrowser.png?raw=true "Screenshot")

## Dependencies

* For the application itself
	* Python 2
	* Python modules:
		* (bottle)[http://bottlepy.org/], required/included
		* (tornado)[http://www.tornadoweb.org/], optional
	* jQuery, required/included
	* vis.js, required/included
* For extracting the key and signature information from the keyserver
  dump files
	* mutt's `pgpring` command

## How it works

1.  Get a dump of the sks keyserver database. The files should be
	named `sks-dump-<nnnn>.pgp`.

	Mirrors to download the dumps can be found e.g.
	[here](https://bitbucket.org/skskeyserver/sks-keyserver/wiki/KeydumpSources).

2.  Extract the signature information from the dump using mutt's
    `pgpring` command (in mutt's debian package to be found in folder
    `/usr/lib/mutt`).

	```
	$ for f in sks-dump-*.pgp; do (pgpring -k $f -S >$f.txt); done
	```

3.  Import the plain text key and signature information to an sqlite database.

	```
	$ python importer.py <path to converted plain text dumps>
	```

4.  Start the backend application and open a browser at http://localhost:8080/

    ```
	$ python server.py
	```

	As the API of the server is quite simple (search keys and get one key,
	there are e.g. no bulk operations), the client performs one HTTP call for
	each retrieved signature of a key.

	To speed up request processing, the server uses the tornado backend by
	default. This can be changed by replacing

	```
	run(host='localhost', port=8080, server="tornado")
	```

	with

	```
	run(host='localhost', port=8080)
	```

	in `server.py`.

5.  Search for an e-mail address (e.g. '%torvalds@%'). The query string is
	passed directly as an argument to an SQL LIKE query, hence wildcards (e.g.
	'%') can be used here.

	**Important**: As the application is for demonstration purposes only, no
	security precautions (query rate limiting, prevention of injection attacks,
	etc.) have been implemented!

	Select an entry from the result list. A node corresponding to the selected
	key/uid along with the primary uid of each signing key shows up.

	Nodes can be expanded via double-clicking to show the primary uids of each
	key which has signed the double-clicked key.

	Keys can be added to the graph via their ID using the "Search by key ID"
	function. Key IDs have to be provided as shown in the search results
	without the leading "0x".

	You can zoom the graph with your mouse's scroll wheel.

	Individual nodes and edges can be removed using the edit bar.

	The parameters of the vis.js' physics engine are explained in [its
	documentation](http://visjs.org/docs/network.html#Physics).

## License

	The MIT License (MIT)

	Copyright (c) 2014 Daniel Wutke

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
