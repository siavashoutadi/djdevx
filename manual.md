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
* `feature`: Add features to your project

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
* `--python-version PATH`: The minimum python version for the project  [default: 3.13]
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

* `all`: Manage all packages at once
* `django-allauth`: Manage django-allauth package
* `django-anymail`: Manage django-anymail package
* `django-auditlog`: Manage django-auditlog package
* `django-browser-reload`: Manage django-browser-reload package
* `django-cors-headers`: Manage django-cors-headers package
* `django-csp`: Manage django-csp package
* `django-debug-toolbar`: Manage django-debug-toolbar package
* `django-defender`: Manage django-defender package
* `django-filter`: Manage django-filter package
* `django-guardian`: Manage django-guardian package
* `django-health-check`: Manage django-health-check package
* `django-oauth-toolkit`: Manage django-oauth-toolkit package
* `django-permissions-policy`: Manage django-permissions-policy package
* `django-role-permissions`: Manage django-role-permissions package
* `django-simple-history`: Manage django-simple-history package
* `django-storages`: Manage django-storages package
* `django-tailwind-cli`: Manage django-tailwind-cli package
* `djangorestframework`: Manage djangorestframework package
* `drf-nested-routers`: Manage drf-nested-routers package
* `drf-spectacular`: Manage drf-spectacular package
* `whitenoise`: Manage whitenoise package

### `djdevx packages all`

Manage all packages at once

**Usage**:

```console
$ djdevx packages all [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure all available packages
* `remove`: Remove all packages

#### `djdevx packages all install`

Install and configure all available packages

**Usage**:

```console
$ djdevx packages all install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages all remove`

Remove all packages

**Usage**:

```console
$ djdevx packages all remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-allauth`

Manage django-allauth package

**Usage**:

```console
$ djdevx packages django-allauth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `remove`: Removing the django-allauth package
* `install`: Installing the django-allauth for...

#### `djdevx packages django-allauth remove`

Removing the django-allauth package

**Usage**:

```console
$ djdevx packages django-allauth remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-allauth install`

Installing the django-allauth for different backends

**Usage**:

```console
$ djdevx packages django-allauth install [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `account`: Installing django-allauth package

##### `djdevx packages django-allauth install account`

Installing django-allauth package

**Usage**:

```console
$ djdevx packages django-allauth install account [OPTIONS]
```

**Options**:

* `--email-subject-prefix TEXT`: Subject-line prefix to use for email messages sent
* `--is-profanity-for-username-enabled / --no-is-profanity-for-username-enabled`: Enable profanity filter for username  [default: is-profanity-for-username-enabled]
* `--account-url-prefix TEXT`: URL prefix for account related URLs  [default: auth]
* `--help`: Show this message and exit.

### `djdevx packages django-anymail`

Manage django-anymail package

**Usage**:

```console
$ djdevx packages django-anymail [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `remove`: Removing the django-anymail package
* `install`: Installing the django-anymail package for...
* `env`: Setting up environment variables for...

#### `djdevx packages django-anymail remove`

Removing the django-anymail package

**Usage**:

```console
$ djdevx packages django-anymail remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-anymail install`

Installing the django-anymail package for different backends

**Usage**:

```console
$ djdevx packages django-anymail install [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ses`: Installing django-anymail with SES backend
* `brevo`: Installing django-anymail with brevo backend
* `mailgun`: Installing django-anymail with mailgun...
* `mailjet`: Installing django-anymail with mailjet...
* `resend`: Installing django-anymail with resend backend

##### `djdevx packages django-anymail install ses`

Installing django-anymail with SES backend

**Usage**:

```console
$ djdevx packages django-anymail install ses [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail install brevo`

Installing django-anymail with brevo backend

**Usage**:

```console
$ djdevx packages django-anymail install brevo [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Brevo API key for authentication  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail install mailgun`

Installing django-anymail with mailgun backend

**Usage**:

```console
$ djdevx packages django-anymail install mailgun [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailgun API key for authentication  [required]
* `--is-europe-region / --no-is-europe-region`: If you are using the Europe region  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail install mailjet`

Installing django-anymail with mailjet backend

**Usage**:

```console
$ djdevx packages django-anymail install mailjet [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailjet API key for authentication  [required]
* `--secret-key TEXT`: The Mailjet secret key for authentication  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail install resend`

Installing django-anymail with resend backend

**Usage**:

```console
$ djdevx packages django-anymail install resend [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Resend API key for authentication  [required]
* `--help`: Show this message and exit.

#### `djdevx packages django-anymail env`

Setting up environment variables for django-anymail package

**Usage**:

```console
$ djdevx packages django-anymail env [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ses`: Creating environment variables for...
* `brevo`: Creating environment variables for...
* `mailgun`: Creating environment variables for...
* `mailjet`: Creating environment variables for...
* `resend`: Creating environment variables for...

##### `djdevx packages django-anymail env ses`

Creating environment variables for django-anymail with SES backend

**Usage**:

```console
$ djdevx packages django-anymail env ses [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail env brevo`

Creating environment variables for django-anymail with brevo backend

**Usage**:

```console
$ djdevx packages django-anymail env brevo [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Brevo API key for authentication  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail env mailgun`

Creating environment variables for django-anymail with mailgun backend

**Usage**:

```console
$ djdevx packages django-anymail env mailgun [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailgun API key for authentication  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail env mailjet`

Creating environment variables for django-anymail with mailjet backend

**Usage**:

```console
$ djdevx packages django-anymail env mailjet [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailjet API key for authentication  [required]
* `--secret-key TEXT`: The Mailjet secret key for authentication  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-anymail env resend`

Creating environment variables for django-anymail with resend backend

**Usage**:

```console
$ djdevx packages django-anymail env resend [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Resend API key for authentication  [required]
* `--help`: Show this message and exit.

### `djdevx packages django-auditlog`

Manage django-auditlog package

**Usage**:

```console
$ djdevx packages django-auditlog [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-auditlog
* `remove`: Remove django-auditlog

#### `djdevx packages django-auditlog install`

Install and configure django-auditlog

**Usage**:

```console
$ djdevx packages django-auditlog install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-auditlog remove`

Remove django-auditlog

**Usage**:

```console
$ djdevx packages django-auditlog remove [OPTIONS]
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

### `djdevx packages django-cors-headers`

Manage django-cors-headers package

**Usage**:

```console
$ djdevx packages django-cors-headers [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-cors-headers
* `remove`: Remove django-cors-headers package

#### `djdevx packages django-cors-headers install`

Install and configure django-cors-headers

**Usage**:

```console
$ djdevx packages django-cors-headers install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-cors-headers remove`

Remove django-cors-headers package

**Usage**:

```console
$ djdevx packages django-cors-headers remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-csp`

Manage django-csp package

**Usage**:

```console
$ djdevx packages django-csp [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-csp
* `remove`: Remove django-csp package

#### `djdevx packages django-csp install`

Install and configure django-csp

**Usage**:

```console
$ djdevx packages django-csp install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-csp remove`

Remove django-csp package

**Usage**:

```console
$ djdevx packages django-csp remove [OPTIONS]
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

### `djdevx packages django-defender`

Manage django-defender package

**Usage**:

```console
$ djdevx packages django-defender [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `env`: Creating environment variables for...
* `install`: Install and configure django-defender
* `remove`: Remove django-defender package

#### `djdevx packages django-defender env`

Creating environment variables for django-defender

**Usage**:

```console
$ djdevx packages django-defender env [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-defender install`

Install and configure django-defender

**Usage**:

```console
$ djdevx packages django-defender install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-defender remove`

Remove django-defender package

**Usage**:

```console
$ djdevx packages django-defender remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-filter`

Manage django-filter package

**Usage**:

```console
$ djdevx packages django-filter [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-filter
* `remove`: Remove django-filter package

#### `djdevx packages django-filter install`

Install and configure django-filter

**Usage**:

```console
$ djdevx packages django-filter install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-filter remove`

Remove django-filter package

**Usage**:

```console
$ djdevx packages django-filter remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-guardian`

Manage django-guardian package

**Usage**:

```console
$ djdevx packages django-guardian [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-guardian
* `remove`: Remove django-guardian

#### `djdevx packages django-guardian install`

Install and configure django-guardian

**Usage**:

```console
$ djdevx packages django-guardian install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-guardian remove`

Remove django-guardian

**Usage**:

```console
$ djdevx packages django-guardian remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-health-check`

Manage django-health-check package

**Usage**:

```console
$ djdevx packages django-health-check [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-health-check
* `remove`: Remove django-health-check

#### `djdevx packages django-health-check install`

Install and configure django-health-check

**Usage**:

```console
$ djdevx packages django-health-check install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-health-check remove`

Remove django-health-check

**Usage**:

```console
$ djdevx packages django-health-check remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-oauth-toolkit`

Manage django-oauth-toolkit package

**Usage**:

```console
$ djdevx packages django-oauth-toolkit [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-oauth-toolkit
* `remove`: Remove django-oauth-toolkit

#### `djdevx packages django-oauth-toolkit install`

Install and configure django-oauth-toolkit

**Usage**:

```console
$ djdevx packages django-oauth-toolkit install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-oauth-toolkit remove`

Remove django-oauth-toolkit

**Usage**:

```console
$ djdevx packages django-oauth-toolkit remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-permissions-policy`

Manage django-permissions-policy package

**Usage**:

```console
$ djdevx packages django-permissions-policy [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure...
* `remove`: Remove django-permissions-policy package

#### `djdevx packages django-permissions-policy install`

Install and configure django-permissions-policy

**Usage**:

```console
$ djdevx packages django-permissions-policy install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-permissions-policy remove`

Remove django-permissions-policy package

**Usage**:

```console
$ djdevx packages django-permissions-policy remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-role-permissions`

Manage django-role-permissions package

**Usage**:

```console
$ djdevx packages django-role-permissions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-role-permissions
* `remove`: Remove django-role-permissions package

#### `djdevx packages django-role-permissions install`

Install and configure django-role-permissions

**Usage**:

```console
$ djdevx packages django-role-permissions install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-role-permissions remove`

Remove django-role-permissions package

**Usage**:

```console
$ djdevx packages django-role-permissions remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-simple-history`

Manage django-simple-history package

**Usage**:

```console
$ djdevx packages django-simple-history [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-simple-history
* `remove`: Remove django-simple-history package

#### `djdevx packages django-simple-history install`

Install and configure django-simple-history

**Usage**:

```console
$ djdevx packages django-simple-history install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-simple-history remove`

Remove django-simple-history package

**Usage**:

```console
$ djdevx packages django-simple-history remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages django-storages`

Manage django-storages package

**Usage**:

```console
$ djdevx packages django-storages [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `remove`: Removing the django-storages package
* `install`: Installing the django-storages for...
* `env`: Setting up environment variables for...

#### `djdevx packages django-storages remove`

Removing the django-storages package

**Usage**:

```console
$ djdevx packages django-storages remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-storages install`

Installing the django-storages for different backends

**Usage**:

```console
$ djdevx packages django-storages install [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `s3`: Installing django-storages package with S3...
* `azure`: Installing django-storages package with...
* `google`: Installing django-storages package with...

##### `djdevx packages django-storages install s3`

Installing django-storages package with S3 backend

**Usage**:

```console
$ djdevx packages django-storages install s3 [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--bucket-name TEXT`: The AWS bucket name to store the files in  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-storages install azure`

Installing django-storages package with Azure backend

**Usage**:

```console
$ djdevx packages django-storages install azure [OPTIONS]
```

**Options**:

* `--account-key TEXT`: The Azure account key for authentication  [required]
* `--account-name TEXT`: The Azure account name for authentication  [required]
* `--container-name TEXT`: The Azure container name to store the files in  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-storages install google`

Installing django-storages package with Google backend

**Usage**:

```console
$ djdevx packages django-storages install google [OPTIONS]
```

**Options**:

* `--credentials-file-path PATH`: The path to the google credential file  [required]
* `--bucket-name TEXT`: The Google bucket name to store the files in  [required]
* `--help`: Show this message and exit.

#### `djdevx packages django-storages env`

Setting up environment variables for django-storages package

**Usage**:

```console
$ djdevx packages django-storages env [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `s3`: Creating environment variables for...
* `azure`: Creating environment variables for...
* `google`: Creating environment variables for...

##### `djdevx packages django-storages env s3`

Creating environment variables for django-storages package with S3 backend

**Usage**:

```console
$ djdevx packages django-storages env s3 [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--bucket-name TEXT`: The AWS bucket name to store the files in  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-storages env azure`

Creating environment variables for django-storages package with Azure backend

**Usage**:

```console
$ djdevx packages django-storages env azure [OPTIONS]
```

**Options**:

* `--account-key TEXT`: The Azure account key for authentication  [required]
* `--account-name TEXT`: The Azure account name for authentication  [required]
* `--container-name TEXT`: The Azure container name to store the files in  [required]
* `--help`: Show this message and exit.

##### `djdevx packages django-storages env google`

Creating environment variables for django-storages package with Google backend

**Usage**:

```console
$ djdevx packages django-storages env google [OPTIONS]
```

**Options**:

* `--credentials-file-path PATH`: The path to the google credential file  [required]
* `--bucket-name TEXT`: The Google bucket name to store the files in  [required]
* `--help`: Show this message and exit.

### `djdevx packages django-tailwind-cli`

Manage django-tailwind-cli package

**Usage**:

```console
$ djdevx packages django-tailwind-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-tailwind-cli
* `remove`: Remove django-tailwind-cli

#### `djdevx packages django-tailwind-cli install`

Install and configure django-tailwind-cli

**Usage**:

```console
$ djdevx packages django-tailwind-cli install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages django-tailwind-cli remove`

Remove django-tailwind-cli

**Usage**:

```console
$ djdevx packages django-tailwind-cli remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages djangorestframework`

Manage djangorestframework package

**Usage**:

```console
$ djdevx packages djangorestframework [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure djangorestframework
* `remove`: Remove djangorestframework

#### `djdevx packages djangorestframework install`

Install and configure djangorestframework

**Usage**:

```console
$ djdevx packages djangorestframework install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages djangorestframework remove`

Remove djangorestframework

**Usage**:

```console
$ djdevx packages djangorestframework remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages drf-nested-routers`

Manage drf-nested-routers package

**Usage**:

```console
$ djdevx packages drf-nested-routers [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure drf-nested-routers
* `remove`: Remove drf-nested-routers package

#### `djdevx packages drf-nested-routers install`

Install and configure drf-nested-routers

**Usage**:

```console
$ djdevx packages drf-nested-routers install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages drf-nested-routers remove`

Remove drf-nested-routers package

**Usage**:

```console
$ djdevx packages drf-nested-routers remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `djdevx packages drf-spectacular`

Manage drf-spectacular package

**Usage**:

```console
$ djdevx packages drf-spectacular [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure drf-spectacular
* `remove`: Remove drf-spectacular package

#### `djdevx packages drf-spectacular install`

Install and configure drf-spectacular

**Usage**:

```console
$ djdevx packages drf-spectacular install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx packages drf-spectacular remove`

Remove drf-spectacular package

**Usage**:

```console
$ djdevx packages drf-spectacular remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

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

## `djdevx feature`

Add features to your project

**Usage**:

```console
$ djdevx feature [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `startapp`: Create a new Django application
* `pwa`: Add PWA support to the project

### `djdevx feature startapp`

Create a new Django application

**Usage**:

```console
$ djdevx feature startapp [OPTIONS]
```

**Options**:

* `--application-name TEXT`: Application name
* `--help`: Show this message and exit.

### `djdevx feature pwa`

Add PWA support to the project

**Usage**:

```console
$ djdevx feature pwa [OPTIONS]
```

**Options**:

* `--name TEXT`: The display name for the application  [required]
* `--short-name TEXT`: The short name for the application when there is not enough space to display the name  [required]
* `--description TEXT`: The description of the application  [required]
* `--icon-path PATH`: Path to the input icon file to be used for generating the PWA icons with different sizes  [default: /tmp/icon.png]
* `--background-color TEXT`: The page color of the window that the application will be opened in  [default: #ffffff]
* `--theme-color TEXT`: The theme color of the application  [default: #000000]
* `--start-url TEXT`: The start URL of the application  [default: /]
* `--dir TEXT`: The base direction of the application  [default: ltr]
* `--scope TEXT`: Defines which URL are within the navigation scope of your application. Scope can often just be set to the base URL of your PWA.
* `--orientation TEXT`: The default orientation of the application. Options are   [default: portrait]
* `--display TEXT`: The display mode that the website should default to. Options are   [default: standalone]
* `--language TEXT`: The primary language of the application  [default: en]
* `--help`: Show this message and exit.
