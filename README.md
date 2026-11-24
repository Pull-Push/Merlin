# Merlin

A real-time chat app with a built-in multi-layer substitution cipher. Everyone in a room agrees on a numeric shift and three code words; messages can be sent encrypted, and anyone holding the same keys can click a message to decode it.

Built with Flask, Flask-SocketIO (WebSockets), MySQL, and vanilla JavaScript.

## Live demo

**https://sokol-merlin-chat-e1b974767f57.herokuapp.com/**

To try it, open the link in two browser windows (one of them private/incognito), create a room in one, join it from the other with the 4-letter code, enter the same four keys in both, and send an encrypted message. If the app has been idle, the first page load may take a few seconds. Rooms are held in memory, so they reset whenever the app restarts.

## Screenshots

| Landing page | Lobby |
<img width="1901" height="957" alt="Screenshot 2026-11-24 at 7 28 46 AM" src="https://github.com/user-attachments/assets/3c105085-106b-402e-b189-d31f8dcf7283" />
| Chat room | Decoding a message |
<img width="1919" height="956" alt="Screenshot 2026-11-24 at 7 31 19 AM" src="https://github.com/user-attachments/assets/c6991d41-5474-4078-bdc1-25fc44a5a4a1" />


## How the cipher works

The keys are four values: a **shift** and three **code words**.

1. **Key generation.** Each of the four values seeds a random number generator. That generator shuffles the printable character set (space, digits, letters, punctuation) into a unique substitution alphabet. The same seed always produces the same shuffle, so no key material is ever stored.
2. **Encoding.** The message passes through all four substitution alphabets in order. The output of layer 1 is the input to layer 2, and so on.
3. **Decoding.** The same four alphabets are applied in reverse order using reverse lookups.

Characters outside the character set (emoji, accented letters) pass through unchanged.

Encryption and decryption happen on the server via `POST /encrypt` and `POST /decrypt`. Keys are rebuilt per request and are never stored or shared between users.

> **Note:** This is a learning project, and the cipher is a layered monoalphabetic substitution. It is fun and hard to casually read, but it is not modern cryptography and shouldn't protect anything sensitive. Chat history is also stored on the server in plaintext (or in whatever form it was sent).

## Features

- Create or join chat rooms with a 4-letter code
- Live messaging over WebSockets
- Send a message encrypted or in the clear
- Click any message to decode it with the keys you've entered
- Room history is replayed when you join
- User registration and login with bcrypt-hashed passwords

## Project structure

```
Merlin/
├── server.py                     # entry point
├── schema.sql                    # MySQL schema
├── requirements.txt
├── .env.example                  # copy to .env
└── flask_app/
    ├── __init__.py               # Flask app + SocketIO instance
    ├── config/mysqlconnection.py # small PyMySQL wrapper
    ├── models/user_model.py      # User queries + validation
    ├── controllers/
    │   ├── user_controller.py    # /, /about, register, login
    │   ├── room_controller.py    # lobby, rooms, socket events
    │   └── encrypt_controller.py # cipher + /encrypt, /decrypt
    ├── templates/                # base, index, home, room, about
    └── static/                   # css/style.css, js/sockscript.js
```

## Running it locally

**Prerequisites:** Python 3.10+ and MySQL 8 (or MariaDB) running locally.

```bash
# 1. Get the code and create a virtual environment
git clone https://github.com/Pull-Push/Merlin.git
cd Merlin
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database
mysql -u root -p < schema.sql

# 4. Configure environment
cp .env.example .env               # then edit .env with your MySQL password
                                   # and a random SECRET_KEY

# 5. Run
python server.py
```

Open **http://localhost:8008**.

Generate a good `SECRET_KEY` with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Trying it out

1. Open the app in two different browsers (or one normal window and one incognito window, so they get separate sessions).
2. In window A, enter a name and click **Create Room**. Note the 4-letter code.
3. In window B, enter a different name and the code, then click **Join Room**.
4. In **both** windows, enter the same keys in the left panel (for example shift `7`, words `alpha`, `beta`, `gamma`).
5. Type in "Type a secret message" and send. It appears scrambled in both windows. Click it to decode it in the bar below.
6. Change one of the code words in window B and click the message again to see what a wrong key produces.

Entering the lobby and joining rooms doesn't require an account. Register and login live on the landing page.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Signs Flask session cookies | placeholder (change it) |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_USER` | MySQL user | `root` |
| `DB_PASSWORD` | MySQL password | empty |
| `DB_NAME` | Database name (overrides `merlin_db`) | `merlin_db` |
| `DB_PORT` | MySQL port | `3306` |
| `PORT` | Server port | `8008` |
| `FLASK_DEBUG` | `1` enables debug/reloader | `0` |

## Troubleshooting

- **`Access denied for user 'root'`**: check `DB_USER` and `DB_PASSWORD` in `.env`.
- **`Unknown database 'merlin_db'`**: you skipped step 3. Run `mysql -u root -p < schema.sql`.
- **`ModuleNotFoundError`**: activate the virtual environment, then rerun `pip install -r requirements.txt`.
- **Messages decode to gibberish**: every participant must use identical keys, including the shift and capitalization of the code words.
- **Rooms disappeared**: room state is in memory, so restarting the server clears all rooms.

## Deploying (Heroku)

The `Procfile` runs gunicorn with one worker and a pool of threads:

```
web: gunicorn --workers 1 --threads 100 server:app
```

`simple-websocket` (in `requirements.txt`) gives Socket.IO real WebSocket support in this mode, so no eventlet or gevent is needed.

- Keep **exactly one** dependency file. Heroku rejects projects that have both `requirements.txt` and a `Pipfile`/`Pipfile.lock`.
- Heroku doesn't include MySQL. Attach a MySQL add-on (JawsDB, ClearDB, etc.) and create the `users` table there using the `CREATE TABLE` statement from `schema.sql`.
- Set config vars instead of using `.env`:
  ```bash
  heroku config:set SECRET_KEY=<random> DB_HOST=<host> DB_USER=<user> \
    DB_PASSWORD=<password> DB_NAME=<dbname> DB_PORT=3306
  ```
- Check startup problems with `heroku logs --tail`.

## Known limitations and roadmap

- **Rooms are stored in memory.** A restart wipes every room and its history. Next step: move rooms and messages to Redis or MySQL.
- **Lobby isn't gated by login.** Anyone can reach `/dashboard`. Next step: a `login_required` decorator, and using the logged-in username as the display name.
- **No CSRF protection** on the forms. Next step: Flask-WTF.
- **Single worker only.** Rooms live in one process's memory, so the app must run with exactly one gunicorn worker and one dyno (see Deploying). Scaling out needs the Redis move above plus a Socket.IO message queue.
- **Keys are typed into the page and sent to the server per request.** A client-side implementation of the cipher would keep keys in the browser entirely.
- Older messages encrypted with the original (pre-refactor) version of the cipher won't decode with this version, because the shuffle is built differently.
