# Project Profiles

Project profiles let you define all the packages, features, frameworks,
database, and cache that a new project should include — then install them all
in one shot with a single command. Profiles are plain TOML files, so they are
easy to share, version in git, and reuse across projects.

## Creating a Project from a Profile

```bash
ddx new --profile multi-page
```

This scaffolds the project and installs everything the profile defines before
the first commit. The `--profile` argument accepts:

- **A built-in profile name** — `multi-page`
- **A local file path** — `./my-profile.toml`
- **A URL** — `https://example.com/profiles/multi-page.toml`
- **A file in a git repo** — `https://github.com/user/profiles.git@multi-page.toml`

Press **Tab** after `ddx new --profile ` to see the available built-in profile
names suggested by the shell. Passing anything else — an unknown built-in name,
an unreadable URL, or a missing file — fails cleanly before any project files
are created; the same applies to `--answers`.

```bash
# Built-in profile
ddx new --profile multi-page

# Local file
ddx new --profile ./team-profile.toml --project-name myproject

# From a git repository (shallow-cloned on the fly)
ddx new --profile https://github.com/acme/django-profiles.git@default.toml
```

### Profile Contents

A profile defines **what to install** in the `[new]`, `[packages]`, `[features]`,
`[frameworks]`, `[database]`, and `[cache]` sections:

```toml
[new]
python_version = "3.14"
git_init = true

[packages]
whitenoise = {}
django-cors-headers = {}
django-allauth = { variants = ["account", "mfa"] }
django-anymail = { variant = "mailgun" }

[features]
pwa = {}

[frameworks]
bootstrap = {}

[database]
postgres = {}

[cache]
redis = {}
```

- `variants` selects **additional** variants for additive installables
  (e.g. allauth's `mfa` on top of the required `account`).
- `variant` selects exactly **one** provider for exclusive installables
  (e.g. anymail's `mailgun`).
- Items with no variants use `{}` and are installed as-is.

### CLI Flags Take Precedence

Project options passed on the command line override profile values:

```bash
# profile says python_version = "3.14"; this overrides it
ddx new --profile multi-page --python-version 3.13
```

The profile is the source of truth for **what** installables get installed —
there are no `--no-<package>` flags.

## Answer Files

Packages with prompts (e.g. the PWA feature, allauth's MFA settings) collect
answers interactively. An **answer file** pre-fills those answers so the
installation can run without prompts:

```toml
# answers.toml
[packages.django-allauth.mfa]
enable_totp = true
enable_webauthn = false
totp_issuer = "MyApp"

[features.pwa]
app_name = "My App"
short_name = "MyApp"
icon_path = "static/images/logo.png"
```

```bash
ddx new --profile ./pwa-profile.toml --answers ./answers.toml
```

When an answer file is provided alongside a profile:

- Values defined in the answer file are used instead of prompting.
- Params **not** in the answer file still prompt interactively.

Answer files accept the same sources as profiles (path, URL, git repo).

## Creating a Profile Interactively

Run `ddx profiles create` from a directory that is **not** a djdevx project to
walk through selecting installables and their options, then write the profile
file:

```bash
ddx profiles create --output my-profile.toml
```

Use the `--interactive` flag to force this flow even inside a project.

For each selected item you will be asked about its variants and parameters.
At the end you can optionally write an **answers file** containing the values
you entered, so the profile can be reused non-interactively. Press `Ctrl+C` at
any prompt to abort the command without writing a profile file.

## Generating a Profile from an Existing Project

Inside a djdevx project (a directory tree containing `djdevx.toml`),
`ddx profiles create` asks whether to generate a profile from the current
project instead of prompting. It reads the project's `djdevx.toml` tracking
state and writes a profile that reproduces its installed configuration:

```bash
cd myproject
ddx profiles create --output myprofile.toml
```

To skip the question and go straight to generation, pass `--from-project`:

```bash
ddx profiles create --from-project
```

## Managing Profiles

```bash
# List built-in profiles
ddx profiles list
```

## Sharing Profiles

Because profiles and answer files are self-contained TOML, they are easy to
share:

- **Commit them to your project** — keep a `ddx-profile.toml` and an
  `answers.toml` in a `profiles/` directory.
- **Publish a git repo of profiles** — point `--profile` at a file inside a
  git repository; djdevx shallow-clones it on demand.
- **Serve them over HTTP** — host `.toml` files and reference them by URL.
- **Copy them anywhere** — a profile is just a file; `ddx new --profile` accepts
  any local path.

## Command Reference

| Command | Purpose |
|---------|---------|
| `ddx new --profile <name\|path\|url>` | Create a project and install a profile |
| `ddx new --profile <p> --answers <a>` | Create from a profile with pre-filled answers |
| `ddx profiles create` | Create a profile (interactively or from the current project) |
| `ddx profiles create --from-project` | Create a profile from the current project |
| `ddx profiles create --interactive` | Create a profile interactively |
| `ddx profiles list` | List built-in profiles |
