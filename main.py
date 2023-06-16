from random import shuffle

from flask import render_template, request, jsonify

from app import *
from db import *


@app.route("/")
def r_index():
    return render_template("index.html", threads=get_all_threads())


@app.route("/t/<thread_id>")
def r_thread(thread_id):
    return render_template("thread.html", thread=get_thread(thread_id))


@app.route("/thread_create", methods=["POST"])
def r_thread_create():
    title = request.json["title"]
    create_thread(title)
    return jsonify({"threads": get_all_threads()})


@app.route("/thread_comment", methods=["POST"])
def r_thread_comment():
    thread_id = request.json["thread_id"]
    parent_id = request.json.get("parent_id")
    comment = request.json["comment"]
    add_comment(thread_id, parent_id, comment)
    return jsonify({"thread": get_thread(thread_id)})


@app.route("/thread_comment_edit", methods=["POST"])
def r_thread_comment_edit():
    thread_id = request.json["thread_id"]
    node_id = request.json["node_id"]
    comment = request.json["comment"]

    edit_comment(thread_id, node_id, comment)

    return jsonify({"thread": get_thread(thread_id)})

@app.route("/thread_comment_delete", methods=["POST"])
def r_thread_comment_delete():
    thread_id = request.json["thread_id"]
    parent_id = request.json.get("parent")
    node_id = request.json["node_id"]

    thread = get_thread(thread_id)

    if parent_id is None:
        parent = thread
    else:
        parent = getNode(thread, parent_id)

    parent["children"] = [child for child in parent["children"] if child["id"] != node_id]

    set_thread(thread)

    return jsonify({"thread": get_thread(thread_id)})

app.run("localhost", 1337, debug=True)
