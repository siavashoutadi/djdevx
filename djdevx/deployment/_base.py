"""BaseDeployPlugin — base class for all deployment target plugins."""

from __future__ import annotations

import inspect
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import typer
from typing_extensions import Annotated

from ..utils.console.print import print_console


@dataclass
class DeployParam:
    """Declares a CLI parameter for ``generate``.

    Each entry becomes a ``--<name>`` option on the auto-generated
    ``generate`` CLI command. Values are forwarded to
    ``plugin.generate(output_dir, **kwargs)``.

    Set ``prompt`` for interactive prompting when the flag is omitted.
    Set ``default=None`` for required parameters.
    """

    name: str
    type_: type = str
    help: str = ""
    default: Any = None
    prompt: str | None = None
    hide_input: bool = False


class BaseDeployPlugin:
    """Base class for deployment manifest generators.

    Subclasses declare:

    * ``name`` — human-readable plugin name (used for default output dir)
    * ``generate_params`` — list of ``DeployParam`` (auto-generates CLI flags)
    * ``generate(output_dir, **kwargs)`` — write manifests
    * ``verify(output_dir) -> bool`` — check manifests are ready
    """

    name: str = ""
    generate_params: list[DeployParam] = []

    # ------------------------------------------------------------------
    # Subclass API
    # ------------------------------------------------------------------

    def generate(self, output_dir: Path, **kwargs: Any) -> None:
        """Generate deployment manifests for this target.

        Args:
            output_dir: Directory to write manifest files into.
            **kwargs: Target-specific CLI parameters declared in
                      ``generate_params``.
        """
        raise NotImplementedError

    def verify(self, output_dir: Path) -> bool:
        """Verify all secrets, configs, and manifests are ready for deployment.

        Return ``True`` if everything is OK, ``False`` otherwise.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # CLI auto-generation
    # ------------------------------------------------------------------

    @property
    def typer_app(self) -> typer.Typer:
        """Return a ``typer.Typer`` with ``generate`` and ``verify`` commands.

        The ``generate`` command's flags are auto-built from
        ``generate_params``.  Each param's name is converted from
        ``snake_case`` to ``--kebab-case`` for the CLI.
        """
        _app = typer.Typer(no_args_is_help=True)

        # -- build generate command signature ---------------------------------
        params: list[inspect.Parameter] = [
            inspect.Parameter(
                "output",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=None,
                annotation=Annotated[
                    Optional[Path],
                    typer.Option(
                        "--output", "-o", help="Output directory for manifests"
                    ),
                ],
            ),
        ]

        for gp in self.generate_params:
            annotation = Annotated[gp.type_, typer.Option(help=gp.help)]  # type: ignore[arg-type]
            params.append(
                inspect.Parameter(
                    gp.name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=gp.default,
                    annotation=annotation,
                )
            )

        def generate_cmd(**cli_kwargs: Any) -> None:
            output_dir = cli_kwargs.pop("output") or self._default_output_dir()
            print_console.step(
                f"Generating {self.name} deployment manifests in {output_dir} \u2026"
            )
            self.generate(output_dir=output_dir, **cli_kwargs)
            print_console.success(f"{self.name} manifests generated.")

        generate_cmd.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]
        generate_cmd.__name__ = "generate"
        _app.command("generate")(generate_cmd)

        # -- build verify command --------------------------------------------
        @_app.command("verify")
        def verify_cmd(
            output: Annotated[
                Optional[Path],
                typer.Option("--output", "-o", help="Output directory for manifests"),
            ] = None,
        ) -> None:
            output_dir = output or self._default_output_dir()
            if not self.verify(output_dir):
                raise typer.Exit(code=1)

        return _app

    # ------------------------------------------------------------------
    # Output directory helpers
    # ------------------------------------------------------------------

    def _default_output_dir(self) -> Path:
        return self._project_root() / "deployment" / self.name.lower().replace(" ", "-")

    @staticmethod
    def _project_root() -> Path:
        from ..utils.djdevx_config.project import ProjectConfig

        return ProjectConfig().project_root_dir

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_files_exist(*paths: Path) -> bool:
        missing = [p for p in paths if not p.exists()]
        if missing:
            for p in missing:
                print_console.error(f"  missing  {p}")
            return False
        return True

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text() == content:
            print_console.info(f"  kept   {path}  (no change)")
            return
        path.write_text(content)
        print_console.info(f"  wrote  {path}")

    @staticmethod
    def _write_once(path: Path, content: str) -> None:
        if path.exists():
            print_console.info(f"  kept   {path}  (no change)")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print_console.info(f"  wrote  {path}  (new)")

    @staticmethod
    def _indent(text: str, spaces: int = 2) -> str:
        return textwrap.indent(text, " " * spaces)

    @staticmethod
    def _to_env_str(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (list, dict)):
            import json

            return json.dumps(value)
        return str(value)
