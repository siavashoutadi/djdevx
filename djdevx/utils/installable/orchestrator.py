"""Orchestrator — centralized add/remove logic for all installable types."""

import sys
from typing import Any

from ..console import prompts
from ..console.print import print_console
from ..tracking import ProjectTracking

from .registry import REGISTRIES
from .resolver import resolve
from .tracking import (
    get_installed_names,
    get_installed_variants,
    get_installable_names,
    get_section,
)
from .types import InstallParam, InstallableRef


def _find_dependents(target_cls) -> list[str]:
    """Display names of installed installables that declare a need for target_cls."""
    project = ProjectTracking()
    target_name = target_cls.get_installable_name()
    dependents: list[str] = []
    for registry in REGISTRIES.values():
        for entry_cls in registry.values():
            if not project.is_installed(
                get_section(entry_cls), entry_cls.get_installable_name()
            ):
                continue
            needs_field = entry_cls.model_fields.get("needs")
            if needs_field is None:
                continue
            needs = needs_field.get_default(call_default_factory=True)
            for ref in needs or []:
                try:
                    resolved = resolve(ref)
                except KeyError:
                    continue
                if resolved.get_installable_name() == target_name:
                    display = entry_cls.model_fields["display_name"].default
                    dependents.append(display or entry_cls.get_installable_name())
                    break
    return sorted(dependents)


def _check_not_needed(installable, name: str) -> bool:
    """Block removal while other installed installables still need this one."""
    dependents = _find_dependents(type(installable))
    if not dependents:
        return True
    print_console.fail(
        f"Cannot remove {installable.display_name or name} — "
        f"required by: {', '.join(dependents)}. Remove them first."
    )
    return False


def _auto_install_needs(needs: list[InstallableRef], verbose: bool) -> None:
    """Resolve and install unmet dependencies recursively."""
    project = ProjectTracking()
    for ref in needs:
        cls = resolve(ref)
        section = get_section(cls)
        if project.is_installed(section, ref.name):
            continue
        print_console.step(f"Installing required dependency: {ref.name}")
        add_installable(cls, ref.name, verbose=verbose)
        print_console.step_done(f"Installed required dependency: {ref.name}")


def select_installable(cls, label: str) -> list[str] | None:
    """Interactive multi-select from not-yet-installed installables."""
    available = get_installable_names(cls)
    if not available:
        print_console.info(f"All {label}s are already installed.")
        return None
    selected = prompts.checkbox(f"Select {label}s to install:", choices=available)
    if not selected:
        print_console.info(f"No {label}s selected.")
        return None
    return selected


def select_installed(cls, label: str) -> list[str] | None:
    """Interactive multi-select from installed installables."""
    installed = get_installed_names(cls)
    if not installed:
        print_console.info(f"No {label}s installed.")
        return None
    selected = prompts.checkbox(
        f"Select {label}s to remove:", choices=sorted(installed)
    )
    if not selected:
        print_console.info(f"No {label}s selected.")
        return None
    return selected


def _prompt_text(param: InstallParam) -> str:
    """Prompt for a text value using questionary."""
    default = str(param.default) if param.default else ""
    if param.hide_input:
        return prompts.password(param.prompt or param.name, default=default) or default
    return prompts.text(param.prompt or param.name, default=default) or default


def _collect_params_interactive(params: list[InstallParam]) -> dict[str, Any]:
    """Collect InstallParam values interactively or use defaults."""
    result: dict[str, Any] = {p.name: p.default for p in params}

    if not sys.stdin.isatty():
        return result

    for param in params:
        if param.show_if is not None or not param.prompt:
            continue
        if param.type_ is bool:
            result[param.name] = prompts.confirm(param.prompt, default=param.default)
        else:
            result[param.name] = _prompt_text(param)

    for param in params:
        if param.show_if is None:
            continue
        gating_value = result.get(param.show_if)
        if gating_value is True and not result[param.name]:
            if param.message_before_prompt:
                import typer

                typer.echo(param.message_before_prompt)
            if param.type_ is bool:
                result[param.name] = prompts.confirm(
                    param.prompt or param.name, default=param.default
                )
            else:
                result[param.name] = _prompt_text(param)

    return result


def _collect_install_kwargs(installable_or_variant) -> dict[str, Any]:
    """Collect interactive install parameters for an installable or variant."""
    if not installable_or_variant.install_params:
        return {}
    return _collect_params_interactive(installable_or_variant.install_params)


def _select_provider(variants: dict) -> str | None:
    """Ask user to pick one variant/provider."""
    choices = [
        prompts.Choice(title=v.display_name, value=k) for k, v in variants.items()
    ]
    return prompts.select("Which provider do you want to use?", choices=choices)


def _select_optional_variants(variants: dict, installed: list[str]) -> list[str] | None:
    """Show checkbox for optional variants not yet installed."""
    optional = [
        prompts.Choice(title=v.display_name, value=k, checked=k in installed)
        for k, v in variants.items()
        if not v.required and k not in installed
    ]
    if not optional:
        return None
    return prompts.checkbox("Which additional functionalities?", choices=optional)


# ------------------------------------------------------------------
# Add
# ------------------------------------------------------------------


def add_installable(
    cls,
    name: str,
    provider: str | None = None,
    verbose: bool = False,
    is_multi: bool = False,
) -> bool:
    """Install an installable.

    Returns True if installed, False if skipped.
    Handles dependencies, variants, and interactive prompts.
    """
    installable = cls(verbose=verbose)

    _auto_install_needs(installable.needs, verbose)

    if installable.exclusive_variants and installable.variants:
        return _add_exclusive_variant(installable, name, provider, verbose, is_multi)

    if installable.variants:
        return _add_additive_variants(installable, name, provider, verbose, is_multi)

    return _add_simple(installable, name, is_multi)


def _add_exclusive_variant(installable, name, provider, verbose, is_multi) -> bool:
    """Install an installable that requires exactly one variant."""
    if name in get_installed_names(type(installable)):
        print_console.ok(f"{installable.display_name} is already installed.")
        return False

    if not provider:
        provider = _select_provider(installable.variants)
        if provider is None:
            return False

    if provider not in installable.variants:
        if is_multi:
            print_console.warning(
                f"Unknown variant '{provider}' "
                f"for {installable.display_name}. Skipping."
            )
            return False
        print_console.fail(f"Unknown variant: {provider}")
        return False

    variant = installable.variants[provider]
    _auto_install_needs(variant.needs, verbose)
    install_kwargs = _collect_install_kwargs(variant)

    print_console.step(f"Installing {installable.display_name}...")
    installable.add(variant_name=provider, install_kwargs=install_kwargs)
    print_console.step_done(
        f"{installable.display_name} ({variant.display_name}) installed."
    )
    return True


def _add_additive_variants(installable, name, provider, verbose, is_multi) -> bool:
    """Install an installable with additive (non-exclusive) variants."""
    installed = get_installed_variants(type(installable), name)

    for rv_name, rv in installable.variants.items():
        if rv.required and rv_name not in installed:
            _auto_install_needs(rv.needs, verbose)
            install_kwargs = _collect_install_kwargs(rv)
            print_console.step(
                f"Installing {installable.display_name} ({rv.display_name})..."
            )
            installable.reset_state()
            installable.add(variant_name=rv_name, install_kwargs=install_kwargs)
            installed.append(rv_name)

    if provider:
        if provider not in installable.variants:
            if is_multi:
                print_console.warning(
                    f"Unknown variant '{provider}' "
                    f"for {installable.display_name}. Skipping."
                )
                return False
            print_console.fail(f"Unknown variant: {provider}")
            return False
        if provider in installed:
            print_console.info(
                f"{installable.variants[provider].display_name} already installed."
            )
            return False
        variant = installable.variants[provider]
        _auto_install_needs(variant.needs, verbose)
        install_kwargs = _collect_install_kwargs(variant)
        print_console.step(
            f"Installing {installable.display_name} ({variant.display_name})..."
        )
        installable.reset_state()
        installable.add(variant_name=provider, install_kwargs=install_kwargs)
    else:
        selected = _select_optional_variants(installable.variants, installed)
        if selected:
            for var_name in selected:
                variant = installable.variants[var_name]
                _auto_install_needs(variant.needs, verbose)
                install_kwargs = _collect_install_kwargs(variant)
                print_console.step(
                    f"Installing {installable.display_name} ({variant.display_name})..."
                )
                installable.reset_state()
                installable.add(variant_name=var_name, install_kwargs=install_kwargs)

    print_console.step_done(f"{installable.display_name} installed.")
    return True


def _add_simple(installable, name, is_multi) -> bool:
    """Install an installable with no variants."""
    if name in get_installed_names(type(installable)):
        print_console.ok(f"{installable.display_name} is already installed.")
        return False

    install_kwargs = _collect_install_kwargs(installable)
    print_console.step(f"Installing {installable.display_name or name}...")
    installable.add(install_kwargs=install_kwargs)
    print_console.step_done(f"{installable.display_name or name} installed.")
    return True


# ------------------------------------------------------------------
# Remove
# ------------------------------------------------------------------


def remove_installable(
    cls,
    name: str,
    provider: str | None = None,
    verbose: bool = False,
    is_multi: bool = False,
) -> bool:
    """Remove an installable.

    Returns True if removed, False if skipped.
    Handles variants and interactive prompts.
    """
    installable = cls(verbose=verbose)

    if name not in get_installed_names(type(installable)):
        if is_multi:
            print_console.warning(
                f"{installable.display_name or name} is not installed. Skipping."
            )
            return False
        print_console.ok(f"{installable.display_name or name} is not installed.")
        return False

    if not _check_not_needed(installable, name):
        return False

    if not installable.variants:
        return _remove_simple(installable, name)

    if installable.exclusive_variants:
        return _remove_exclusive_variant(installable, name, provider, is_multi)

    return _remove_additive_variants(installable, name, provider, is_multi)


def _remove_simple(installable, name) -> bool:
    """Remove an installable with no variants."""
    print_console.step(f"Removing {installable.display_name or name}...")
    installable.remove()
    print_console.step_done(f"{installable.display_name or name} removed.")
    return True


def _remove_exclusive_variant(installable, name, provider, is_multi) -> bool:
    """Remove an installable with exclusive variants."""
    if provider:
        if provider not in get_installed_variants(type(installable), name):
            if is_multi:
                print_console.warning(
                    f"Variant '{provider}' is not installed. Skipping."
                )
                return False
            print_console.warning(f"Variant '{provider}' is not installed.")
            return False
        variant = installable.variants[provider]
        print_console.step(
            f"Removing {installable.display_name} ({variant.display_name})..."
        )
        installable.remove(variant_name=provider)
    else:
        print_console.step(f"Removing {installable.display_name or name}...")
        installable.remove()
    print_console.step_done(f"{installable.display_name or name} removed.")
    return True


def _remove_additive_variants(installable, name, provider, is_multi) -> bool:
    """Remove an installable with additive variants."""
    if provider:
        if provider not in get_installed_variants(type(installable), name):
            if is_multi:
                print_console.warning(
                    f"Variant '{provider}' is not installed. Skipping."
                )
                return False
            print_console.warning(f"Variant '{provider}' is not installed.")
            return False
        variant = installable.variants[provider]
        print_console.step(
            f"Removing {installable.display_name} ({variant.display_name})..."
        )
        installable.remove(variant_name=provider)
        print_console.step_done(f"{installable.display_name or name} removed.")
        return True

    installed_variants = get_installed_variants(type(installable), name)
    choices = [
        prompts.Choice(title=installable.variants[v].display_name, value=v)
        for v in installed_variants
    ]
    selected = prompts.checkbox("Which variants to remove?", choices=choices)
    if not selected:
        print_console.info("No variants selected.")
        return False
    for var_name in selected:
        variant = installable.variants[var_name]
        print_console.step(
            f"Removing {installable.display_name} ({variant.display_name})..."
        )
        installable.reset_state()
        installable.remove(variant_name=var_name)
    return True
