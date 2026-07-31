# djdevx

**Usage**:

```console
$ djdevx [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `version`: Show the application version
* `requirement`: Check system requirements
* `new`: Create a new project
* `packages`: Manage Django packages
* `frameworks`: Manage CSS/JS frameworks
* `features`: Manage features
* `create`: Create new Django applications
* `database`: Manage database infrastructure
* `cache`: Manage cache infrastructure
* `settings`: Manage project secrets and configs
* `deployment`: Generate deployment manifests

## djdevx version

Show the application version

**Usage**:

```console
$ djdevx version [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

## djdevx requirement

Check system requirements

**Usage**:

```console
$ djdevx requirement [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `verify`: Check the requirements for project creation.

## djdevx requirement verify

Check the requirements for project creation.

**Usage**:

```console
$ djdevx requirement verify [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## djdevx new

Create a new project

**Usage**:

```console
$ djdevx new [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--project-name TEXT`: The name of the project  [default: my-project]
* `--project-description TEXT`: The description of the project  [default: My project is awesome]
* `--project-directory PATH`: The directory to initialize the project in  [default: .]
* `--python-version TEXT`: The minimum python version for the project  [default: 3.14]
* `--git-init / --no-git-init`: whether to initialize a git repository in the project directory  [default: git-init]
* `-v, --verbose`: Show full output of all commands
* `--help`: Show this message and exit.

## djdevx packages

Manage Django packages

**Usage**:

```console
$ djdevx packages [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Install a package.
* `remove`: Remove a package or variant.
* `list`: List all available packages with install...

## djdevx packages add

Install a package.

**Usage**:

```console
$ djdevx packages add [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Package name to install

**Options**:

* `-p, --provider TEXT`: Variant/provider name
* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx packages remove

Remove a package or variant.

**Usage**:

```console
$ djdevx packages remove [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Package name to remove

**Options**:

* `-p, --provider TEXT`: Variant/provider to remove
* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx packages list

List all available packages with install status in a table.

**Usage**:

```console
$ djdevx packages list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## djdevx frameworks

Manage CSS/JS frameworks

**Usage**:

```console
$ djdevx frameworks [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a CSS/JS framework.
* `remove`: Remove a CSS/JS framework.
* `list`: List all available frameworks with install...

## djdevx frameworks add

Add a CSS/JS framework.

**Usage**:

```console
$ djdevx frameworks add [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Framework name to add

**Options**:

* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx frameworks remove

Remove a CSS/JS framework.

**Usage**:

```console
$ djdevx frameworks remove [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Framework name to remove

**Options**:

* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx frameworks list

List all available frameworks with install status in a table.

**Usage**:

```console
$ djdevx frameworks list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## djdevx features

Manage features

**Usage**:

```console
$ djdevx features [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Install a feature.
* `remove`: Remove a feature or variant.
* `list`: List all available features with install...

## djdevx features add

Install a feature.

**Usage**:

```console
$ djdevx features add [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Feature name to install

**Options**:

* `-p, --provider TEXT`: Variant/provider name
* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx features remove

Remove a feature or variant.

**Usage**:

```console
$ djdevx features remove [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Feature name to remove

**Options**:

* `-p, --provider TEXT`: Variant/provider to remove
* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx features list

List all available features with install status in a table.

**Usage**:

```console
$ djdevx features list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## djdevx create

Create new Django applications

**Usage**:

```console
$ djdevx create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `app`: Create a new Django application.

## djdevx create app

Create a new Django application.

**Usage**:

```console
$ djdevx create app [OPTIONS]
```

**Options**:

* `--name TEXT`: Application name
* `--help`: Show this message and exit.

## djdevx database

Manage database infrastructure

**Usage**:

```console
$ djdevx database [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a database.
* `remove`: Remove a database.
* `list`: List all available databases with install...

## djdevx database add

Add a database.

**Usage**:

```console
$ djdevx database add [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Database provider name to install

**Options**:

* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx database remove

Remove a database.

**Usage**:

```console
$ djdevx database remove [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Database provider name to remove

**Options**:

* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx database list

List all available databases with install status in a table.

**Usage**:

```console
$ djdevx database list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## djdevx cache

Manage cache infrastructure

**Usage**:

```console
$ djdevx cache [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a cache.
* `remove`: Remove a cache.
* `list`: List all available caches with install...

## djdevx cache add

Add a cache.

**Usage**:

```console
$ djdevx cache add [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Cache provider name to install

**Options**:

* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx cache remove

Remove a cache.

**Usage**:

```console
$ djdevx cache remove [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Cache provider name to remove

**Options**:

* `-v, --verbose`: Show full pixi output
* `--help`: Show this message and exit.

## djdevx cache list

List all available caches with install status in a table.

**Usage**:

```console
$ djdevx cache list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## djdevx settings

Manage project secrets and configs

**Usage**:

```console
$ djdevx settings [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `secrets`: Manage project secrets
* `configs`: Manage project config variables

## djdevx settings secrets

Manage project secrets

**Usage**:

```console
$ djdevx settings secrets [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List secrets for the given environment.
* `init`: Initialize secrets for the given environment.
* `verify`: Verify secrets completeness.

## djdevx settings secrets list

List secrets for the given environment.

**Usage**:

```console
$ djdevx settings secrets list [OPTIONS] ENV:{dev|prod}
```

**Arguments**:

* `ENV:{dev|prod}`: Environment: dev or prod  [required]

**Options**:

* `--help`: Show this message and exit.

## djdevx settings secrets init

Initialize secrets for the given environment.

**Usage**:

```console
$ djdevx settings secrets init [OPTIONS] ENV:{dev|prod}
```

**Arguments**:

* `ENV:{dev|prod}`: Environment: dev or prod  [required]

**Options**:

* `--help`: Show this message and exit.

## djdevx settings secrets verify

Verify secrets completeness.

**Usage**:

```console
$ djdevx settings secrets verify [OPTIONS] ENV:{dev|prod}
```

**Arguments**:

* `ENV:{dev|prod}`: Environment: dev or prod  [required]

**Options**:

* `--help`: Show this message and exit.

## djdevx settings configs

Manage project config variables

**Usage**:

```console
$ djdevx settings configs [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List config vars for the given environment.
* `init`: Initialize config vars for the given...
* `verify`: Verify config vars completeness.

## djdevx settings configs list

List config vars for the given environment.

**Usage**:

```console
$ djdevx settings configs list [OPTIONS] ENV:{dev|prod}
```

**Arguments**:

* `ENV:{dev|prod}`: Environment: dev or prod  [required]

**Options**:

* `--help`: Show this message and exit.

## djdevx settings configs init

Initialize config vars for the given environment.

**Usage**:

```console
$ djdevx settings configs init [OPTIONS] ENV:{dev|prod}
```

**Arguments**:

* `ENV:{dev|prod}`: Environment: dev or prod  [required]

**Options**:

* `--help`: Show this message and exit.

## djdevx settings configs verify

Verify config vars completeness.

**Usage**:

```console
$ djdevx settings configs verify [OPTIONS] ENV:{dev|prod}
```

**Arguments**:

* `ENV:{dev|prod}`: Environment: dev or prod  [required]

**Options**:

* `--help`: Show this message and exit.

## djdevx deployment

Generate deployment manifests

**Usage**:

```console
$ djdevx deployment [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `docker-compose`: Docker Compose: generate manifests + verify

## djdevx deployment docker-compose

Docker Compose: generate manifests + verify

**Usage**:

```console
$ djdevx deployment docker-compose [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `generate`
* `verify`

## djdevx deployment docker-compose generate

**Usage**:

```console
$ djdevx deployment docker-compose generate [OPTIONS]
```

**Options**:

* `-o, --output PATH`: Output directory for manifests
* `--domain TEXT`: Domain name for the deployment
* `--traefik-email TEXT`: Email for Let&#x27;s Encrypt certificates
* `--cloudflare-token TEXT`: CF_DNS_API_TOKEN for Cloudflare DNS challenge (optional)
* `--help`: Show this message and exit.

## djdevx deployment docker-compose verify

**Usage**:

```console
$ djdevx deployment docker-compose verify [OPTIONS]
```

**Options**:

* `-o, --output PATH`: Output directory for manifests
* `--help`: Show this message and exit.
