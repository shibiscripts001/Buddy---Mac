# Buddy Network server

The chat server Buddy's **Buddy Network** page connects to. It's a separate
program: not part of buddy.zip or the installer. Buddy connects to the public
server (`DEFAULT_SERVER_URL` in `app/core/buddy_server.py`) unless a different
address is set in Settings, so you only need this to run a server of your own.

It keeps no IP addresses: not in its database, and not in its logs.

## Try it on this computer

1. Once: `pip install -r server/requirements.txt` (just `websockets`).
2. From the repo folder: `python -m server --dev`
   - It listens on `ws://localhost:8765`.
   - `--dev` lifts the limit of 3 new identities per address per day.
     Every test identity comes from this computer, so without it the fourth
     one would be refused.
   - Messages go in `buddy_network.db` in the current folder. Delete it to
     start over.
3. In Buddy, set Buddy Network's server address (Settings) to
   `ws://localhost:8765`, then open **Buddy Network** (bottom of the rail)
   and turn it on. Clear the address again to go back to the public server.
4. To chat with yourself (a second Buddy can't run on the same computer),
   open another terminal and run `python -m server.tryout --name Sam`. It
   joins #Global as a second person: type a line to send it, and it prints
   what Buddy sends. Add `--room help` for the Help room.

Stop the server with Ctrl+C.

## Making yourself the owner

1. In Buddy, open Buddy Network > Account and copy your ID.
2. `python -m server make-owner <your ID> --db buddy_network.db` (use the
   same `--db` the server runs with). The server can keep running.
3. Turn Buddy Network off and on (or restart Buddy) to pick it up: an
   **Admin** button appears, and you can make other people mods or admins
   there (Staff tab, or click their name). Admins can make mods too.

`python -m server set-role <ID> user` takes a role away again.

## Hosting your own

On a fresh Ubuntu 24.04 server with a domain pointed at it:

1. `bash server/deploy/push.sh root@<server address>` copies the code over.
2. On the server, as root:
   `bash /opt/buddy-network/server/deploy/setup.sh <your domain>` - installs
   the service, Caddy for https/wss with a Let's Encrypt certificate, a
   firewall, key-only SSH and nightly database backups. Safe to run again.
3. In Buddy, set the server address (Settings) to `wss://<your domain>`.

Run `push.sh` again to update the code; it restarts the service.

## Files

| File | What it does |
|---|---|
| `core.py` | All the rules: identity, names, rooms, sending, deleting, limits. No network code, so `tests/test_network_server.py` drives it directly. |
| `store.py` | SQLite tables: users, rooms, messages. No IP addresses. |
| `net.py` | The WebSocket side: passes each frame to `core.py`. Also answers `GET /announcements.json`, the app announcements shown in Buddy. |
| `__main__.py` | `python -m server` options. |
| `social.py` | Buddies, DMs, blocking, deleting an account. |
| `admin.py` | Reports, bans, roles, the admin log. |
| `common.py` | The shapes users, rooms and messages take on the wire. |
| `tryout.py` | The terminal chatter from step 4. |
| `deploy/` | `push.sh` and `setup.sh` (see Hosting your own), `hardening.conf` for the service. |
