from time import time
import uuid
from copy import deepcopy
import json

import dataset
from flask import g

from app import *

"""
If it doesn't exist yet, Dataset will create a new file, database.db in this directory
Together with the database.db-shm and database.db-wal files
which are created on reads and writes (do not delete these!), it makes up the database
Open database.db with DB Browser for SQLite to inspect its contents
You can copy these three files somewhere to make a backup of your database
"""

DATABASE = "sqlite:///database.db?check_same_thread=False"

def get_threads():
	"""can be called by any function to get access to the database table called 'mytable'"""

	db = getattr(g, "_database", None)

	if db is None:
		db = g._database = dataset.connect(DATABASE)

	return db["threads"]

"""
We are using the database here to store some previous calculation results, but it could be anything!
some data you collected yourself, user generated content, user accounts...

Just create a new get_<tablename> function for each new table and use them in your new functions
"""

def create_thread(title):
	"""creates a new row in the database. dataset will insert columns automatically if they don't exist yet
	the same goes for the table and the database file"""

	threads = get_threads()

	thread = {
		"created": time(),
		"title": title,
		"children": json.dumps([])
	}

	threads.insert(thread)


def get_all_threads():
	threads = get_threads()
	return list(threads.all())


def get_thread(thread_id):
	"""will return None if no row with that input"""

	threads = get_threads()

	thread = threads.find_one(id=thread_id)

	if thread is None:
		return None

	thread["children"] = json.loads(thread["children"])

	return thread


def set_thread(thread):
	# Copy here so calling function can still use unstringified json
	threadcopy = deepcopy(thread)

	threadcopy["children"] = json.dumps(thread["children"])

	threads = get_threads()
	threads.update(threadcopy, ["id"])


def get_comment(comments, comment_id):
	for child in comments["children"]:
		if child["id"] == comment_id:
			return child
		else:
			result = get_comment(child, comment_id)
			if result is not None:
				return result


def add_comment(thread_id, parent_id, comment):
	thread = get_thread(thread_id)

	new_comment = {"id": str(uuid.uuid4()), "comment": comment, "children": []}

	if parent_id is None:
		thread["children"].append(new_comment)
	else:
		parent = get_comment(thread, parent_id)
		parent["children"].append(new_comment)
		print("PARENT", parent)
	print(thread)

	set_thread(thread)


def edit_comment(thread_id, node_id, comment):
	thread = get_thread(thread_id)

	node = get_comment(thread, node_id)
	node["comment"] = comment

	set_thread(thread)

"""
Utility to execute requests interactively

$ python
>>> from db import *
>>> with_context(set_cache, 2, 4)
>>> with_context(get_cache, 2)
4.0
"""
def with_context(f, *args, **kwargs):
    with app.app_context():
        return f(*args, **kwargs)
