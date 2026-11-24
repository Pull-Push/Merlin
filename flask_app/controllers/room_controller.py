from flask_app import app, socketio
from flask import render_template, request, redirect, session, url_for
from flask_socketio import join_room, leave_room, send
import random
from string import ascii_uppercase
from flask_app.controllers import encrypt_controller  # noqa: F401 - registers routes

rooms = {}


def generate_unique_code(length=4):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code


@app.route("/dashboard", methods=["POST", "GET"])
def roomreg():
    session.clear()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip().upper()
        joining = request.form.get("join") is not None
        creating = request.form.get("create") is not None

        if not name:
            return render_template("home.html", error="Please enter a name", code=code, name=name)
        if joining and not code:
            return render_template("home.html", error="Please enter a room code", code=code, name=name)

        if creating:
            room = generate_unique_code()
            rooms[room] = {"members": 0, "messages": []}
        else:
            if code not in rooms:
                return render_template("home.html", error="Room not found. Check your code.", code=code, name=name)
            room = code

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")


@app.route("/room")
def room():
    room = session.get("room")
    if not room or not session.get("name") or room not in rooms:
        return redirect("/dashboard")
    return render_template("room.html", room=room, messages=rooms[room]["messages"])


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    if not room or not name or room not in rooms:
        leave_room(room)
        return

    join_room(room)
    rooms[room]["members"] += 1
    send({"name": name, "message": "has entered the room"}, to=room)
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")

    if room:
        leave_room(room)
        if room in rooms:
            rooms[room]["members"] -= 1
            if rooms[room]["members"] <= 0:
                del rooms[room]
        send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} left room {room}")


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"],
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{content['name']} said: {content['message']}")
