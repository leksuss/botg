from fabric import Connection, task

PROJECT_DIR = "/opt/django-telegram-starter"  # поменяйте под свой путь на сервере
DEFAULT_HOST = "prod"  # можно вызывать с -H для другого хоста
SERVICE_NAME = "django_telegram_starter"


def _get_conn(c):
    if getattr(c, "host", None):
        return c
    return Connection(DEFAULT_HOST, forward_agent=True)


def _compose_cmd(c):
    c = _get_conn(c)
    if c.run("docker compose version", hide=True, warn=True).ok:
        return "docker compose"
    return "docker-compose"


@task
def pull(c, branch="main"):
    """Fetch latest code and hard reset to remote branch."""
    c = _get_conn(c)
    with c.cd(PROJECT_DIR):
        c.run("git fetch --all")
        c.run(f"git reset --hard origin/{branch}")


@task
def build(c, pull_base=True):
    """Build images using docker compose (optionally pulling base layers)."""
    c = _get_conn(c)
    compose = _compose_cmd(c)
    pull_flag = " --pull" if pull_base else ""
    c.sudo(
        f"bash -lc 'cd {PROJECT_DIR} && {compose} build{pull_flag}'",
        pty=True,
    )


@task
def migrate(c):
    """Run Django migrations inside the web service container."""
    c = _get_conn(c)
    compose = _compose_cmd(c)
    c.sudo(
        f"bash -lc 'cd {PROJECT_DIR} && {compose} run --rm web python src/manage.py migrate --noinput'",
        pty=True,
    )


@task
def restart(c):
    """Restart the systemd service managing the app stack."""
    c = _get_conn(c)
    c.sudo(f"systemctl restart {SERVICE_NAME}", pty=True)


@task
def deploy(c, branch="main"):
    """Full deployment pipeline: pull -> build -> migrate -> restart."""
    c = _get_conn(c)
    pull(c, branch=branch)
    build(c)
    migrate(c)
    restart(c)
