# `djdevx`

**Usage**:

```console
$ djdevx [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `version`: Show the application version.
* `requirement`: Check the requirement for project creation.
* `init`: Initialize the project
* `packages`: Install and configure django packages

## `djdevx version`

Show the application version.

**Usage**:

```console
$ djdevx version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `djdevx requirement`

Check the requirement for project creation.

**Usage**:

```console
$ djdevx requirement [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `djdevx init`

Initialize the project

**Usage**:

```console
$ djdevx init [OPTIONS]
```

**Options**:

* `--project-name TEXT`: The name of the project  [default: my-project]
* `--project-description TEXT`: The description of the project  [default: My project is awesome]
* `--project-directory PATH`: The directory to initialize the project in  [default: .]
* `--git-init / --no-git-init`: whether to initialize a git repository in the project directory  [default: git-init]
* `--help`: Show this message and exit.

## `djdevx packages`

Install and configure django packages

**Usage**:

```console
$ djdevx packages [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `whitenoise`: Manage whitenoise package
* `django-browser-reload`: Manage django-browser-reload package
* `django-debug-toolbar`: Manage django-debug-toolbar package

### `djdevx packages whitenoise`

Manage whitenoise package

**Usage**:

```console
$ djdevx packages whitenoise [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure whitenoise
* `remove`: Remove whitenoise

#### `djdevx packages whitenoise install`

Install and configure whitenoise

**Usage**:

```console
$ djdevx packages whitenoise install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages whitenoise remove`

Remove whitenoise

**Usage**:

```console
$ djdevx packages whitenoise remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-browser-reload`

Manage django-browser-reload package

**Usage**:

```console
$ djdevx packages django-browser-reload [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-browser-reload
* `remove`: Remove django-browser-reload

#### `djdevx packages django-browser-reload install`

Install and configure django-browser-reload

**Usage**:

```console
$ djdevx packages django-browser-reload install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-browser-reload remove`

Remove django-browser-reload

**Usage**:

```console
$ djdevx packages django-browser-reload remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-debug-toolbar`

Manage django-debug-toolbar package

**Usage**:

```console
$ djdevx packages django-debug-toolbar [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-debug-toolbar
* `remove`: Remove django-debug-toolbar

#### `djdevx packages django-debug-toolbar install`

Install and configure django-debug-toolbar

**Usage**:

```console
$ djdevx packages django-debug-toolbar install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-debug-toolbar remove`

Remove django-debug-toolbar

**Usage**:

```console
$ djdevx packages django-debug-toolbar remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
