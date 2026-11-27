"""Typed local postproduction CLI; import/help never installs, publishes, uploads or launches a user app."""
from pydantic import ValidationError
import typer

from postproduction.cli_environment import register as environment_commands
from postproduction.cli_project import register as project_commands
from postproduction.cli_support import CliError
from postproduction.cli_work import register as work_commands
from postproduction.errors import ContractError

app = typer.Typer(add_completion=False,no_args_is_help=True,help="Local source-grounded postproduction; install requires inspect → actual question → exact consent.")
environment_commands(app)
project_commands(app)
work_commands(app)


def main() -> int:
    try:
        app()
    except ContractError as exc:
        typer.echo(CliError(error=str(exc),stage=exc.stage).model_dump_json(),err=True)
        return 1
    except (OSError,ValidationError,ValueError) as exc:
        typer.echo(CliError(error=str(exc),stage="input").model_dump_json(),err=True)
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
