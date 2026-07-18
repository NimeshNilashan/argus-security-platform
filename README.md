# argus-security-platform

Issues and challenges I have faced during the development of this project

**Problems faced so far — environment & infrastructure setup**

* Couldn't locate the WSL home folder in File Explorer — was using a placeholder path instead of the actual distro name (`Ubuntu-22.04`) and username (`nimesh`)
* PyCharm's WSL interpreter setup initially created a virtualenv tied to the wrong project (a blank default project instead of the actual capstone folder)
* New PyCharm terminals weren't auto-activating the project's virtualenv, requiring manual `source` activation
* Docker CLI wasn't accessible from inside WSL despite Docker Desktop running — WSL integration toggle for the specific distro wasn't actually taking effect
* Resolving the Docker integration required a full Windows reboot, not just `wsl --shutdown` — a stale Docker Desktop background service was the root cause
* Docker Compose's bind mount (`.:/app`) wasn't syncing files in either direction between host and container — caused by the container having been created before the volume was properly configured; required a full `docker compose down` + rebuild
* An `alembic init` run before the bind mount was fixed created files only inside the container's temporary layer — that entire `migrations` folder was permanently lost when the container was recreated
* Files generated inside the container (`alembic.ini`) came out root-owned, blocking PyCharm from editing them — required `chown` to reclaim ownership
* Alembic's `env.py` was reading a stale/incorrect database URL from `alembic.ini` instead of the app's real `DATABASE_URL` environment variable, causing a password authentication failure during migrations
* PyCharm's Database tool was only showing the default `postgres` system database — the actual `argus_security_capstone` database was hidden until manually enabled in the data source's schema visibility settings
* SQLAlchemy database connection issue
    - Error occurred when creating SQLAlchemy engine:
    - Expected string or URL object, got PostgresDsn
    - Identified that Pydantic converted DATABASE_URL into a PostgresDsn object.
    - Fixed compatibility issue by converting the URL object into a string before passing it to SQLAlchemy.