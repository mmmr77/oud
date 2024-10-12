
from dynaconf import Dynaconf

settings = Dynaconf(
    load_dotenv=True,
    dotenv_override=True,
    envvar_prefix=False,
    settings_files=['settings.toml'],
)
