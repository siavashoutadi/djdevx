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
* `new`: Create a new project
* `backend`: Backend development tools

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

## `djdevx new`

Create a new project

**Usage**:

```console
$ djdevx new [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `backend`: Create a backend only project

### `djdevx new backend`

Create a backend only project

**Usage**:

```console
$ djdevx new backend [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `django`: Create a new django project

#### `djdevx new backend django`

Create a new django project

**Usage**:

```console
$ djdevx new backend django [OPTIONS]
```

**Options**:

* `--project-name TEXT`: The name of the project  [default: my-project]
* `--project-description TEXT`: The description of the project  [default: My project is awesome]
* `--project-directory PATH`: The directory to initialize the project in  [default: .]
* `--python-version TEXT`: The minimum python version for the project  [default: 3.14]
* `--backend-root TEXT`: Backend root directory name  [default: backend]
* `--git-init / --no-git-init`: whether to initialize a git repository in the project directory  [default: git-init]
* `--help`: Show this message and exit.

## `djdevx backend`

Backend development tools

**Usage**:

```console
$ djdevx backend [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `django`: Django backend development tools

### `djdevx backend django`

Django backend development tools

**Usage**:

```console
$ djdevx backend django [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `packages`: Install and configure django packages
* `feature`: Add features to your Django project
* `create`: Create new Django applications or components

#### `djdevx backend django packages`

Install and configure django packages

**Usage**:

```console
$ djdevx backend django packages [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `channels`: Manage channels package
* `django-allauth`: Manage django-allauth package
* `django-anymail`: Manage django-anymail package
* `django-auditlog`: Manage django-auditlog package
* `django-browser-reload`: Manage django-browser-reload package
* `django-cors-headers`: Manage django-cors-headers package
* `django-csp`: Manage django-csp package
* `django-debug-toolbar`: Manage django-debug-toolbar package
* `django-defender`: Manage django-defender package
* `django-extensions`: Manage django-extensions package
* `django-filter`: Manage django-filter package
* `django-guardian`: Manage django-guardian package
* `django-health-check`: Manage django-health-check package
* `django-meta`: Manage django-meta package
* `django-oauth-toolkit`: Manage django-oauth-toolkit package
* `django-permissions-policy`: Manage django-permissions-policy package
* `django-role-permissions`: Manage django-role-permissions package
* `django-simple-history`: Manage django-simple-history package
* `django-snakeoil`: Manage django-snakeoil package
* `django-storages`: Manage django-storages package
* `django-taggit`: Manage django-taggit package
* `django-tailwind-cli`: Manage django-tailwind-cli package
* `heroicons`: Manage heroicons package
* `djangochannelsrestframework`: Manage djangochannelsrestframework package
* `djangorestframework`: Manage djangorestframework package
* `drf-nested-routers`: Manage drf-nested-routers package
* `drf-flex-fields`: Manage drf-flex-fields package
* `drf-spectacular`: Manage drf-spectacular package
* `whitenoise`: Manage whitenoise package

##### `djdevx backend django packages channels`

Manage channels package

**Usage**:

```console
$ djdevx backend django packages channels [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `env`: Creating environment variables for channels
* `install`: Install and configure channels
* `remove`: Remove channels package

###### `djdevx backend django packages channels env`

Creating environment variables for channels

**Usage**:

```console
$ djdevx backend django packages channels env [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages channels install`

Install and configure channels

**Usage**:

```console
$ djdevx backend django packages channels install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages channels remove`

Remove channels package

**Usage**:

```console
$ djdevx backend django packages channels remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-allauth`

Manage django-allauth package

**Usage**:

```console
$ djdevx backend django packages django-allauth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `account`: Manage django-allauth with account...
* `mfa`: Manage django-allauth with MFA functionality
* `oidc-provider`: Manage django-allauth with OIDC provider...

###### `djdevx backend django packages django-allauth account`

Manage django-allauth with account functionality

**Usage**:

```console
$ djdevx backend django packages django-allauth account [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-allauth package with...
* `remove`: Remove django-allauth account functionality
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-allauth account install`

Install django-allauth package with account functionality

**Usage**:

```console
$ djdevx backend django packages django-allauth account install [OPTIONS]
```

**Options**:

* `--email-subject-prefix TEXT`: Subject-line prefix to use for email messages sent
* `--enable-login-by-code / --no-enable-login-by-code`: Enable login by code  [default: enable-login-by-code]
* `--is-profanity-for-username-enabled / --no-is-profanity-for-username-enabled`: Enable profanity filter for username  [default: is-profanity-for-username-enabled]
* `--account-url-prefix TEXT`: URL prefix for account related URLs  [default: auth]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-allauth account remove`

Remove django-allauth account functionality

**Usage**:

```console
$ djdevx backend django packages django-allauth account remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-allauth account env`

Configure environment variables for django-allauth

**Usage**:

```console
$ djdevx backend django packages django-allauth account env [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-allauth mfa`

Manage django-allauth with MFA functionality

**Usage**:

```console
$ djdevx backend django packages django-allauth mfa [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-allauth package with MFA...
* `remove`: Remove django-allauth MFA configuration

####### `djdevx backend django packages django-allauth mfa install`

Install django-allauth package with MFA functionality

**Usage**:

```console
$ djdevx backend django packages django-allauth mfa install [OPTIONS]
```

**Options**:

* `--enable-totp / --no-enable-totp`: Enable TOTP authentication  [default: enable-totp]
* `--enable-recovery-codes / --no-enable-recovery-codes`: Enable recovery codes  [default: enable-recovery-codes]
* `--enable-webauthn / --no-enable-webauthn`: Enable WebAuthn/passkeys authentication  [default: no-enable-webauthn]
* `--enable-trust / --no-enable-trust`: Enable &#x27;trust this browser&#x27; functionality  [default: no-enable-trust]
* `--totp-issuer TEXT`: Issuer name for TOTP QR codes
* `--totp-period INTEGER RANGE`: TOTP token validity period in seconds  [default: 30; 15&lt;=x&lt;=300]
* `--totp-digits INTEGER RANGE`: Number of digits in TOTP tokens  [default: 6; 6&lt;=x&lt;=8]
* `--totp-tolerance INTEGER RANGE`: TOTP time tolerance (number of periods to allow)  [default: 0; 0&lt;=x&lt;=5]
* `--recovery-code-count INTEGER RANGE`: Number of recovery codes to generate  [default: 10; 5&lt;=x&lt;=20]
* `--recovery-code-digits INTEGER RANGE`: Number of digits in each recovery code  [default: 8; 6&lt;=x&lt;=16]
* `--passkey-login / --no-passkey-login`: Enable passkey login  [default: no-passkey-login]
* `--passkey-signup / --no-passkey-signup`: Enable passkey signup  [default: no-passkey-signup]
* `--webauthn-allow-insecure / --no-webauthn-allow-insecure`: Allow WebAuthn over insecure origins (for development)  [default: no-webauthn-allow-insecure]
* `--trust-cookie-age-days INTEGER RANGE`: Trust cookie validity period in days  [default: 14; 1&lt;=x&lt;=365]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-allauth mfa remove`

Remove django-allauth MFA configuration

Note: This removes MFA configuration but keeps the django-allauth
package installed with its dependencies. To completely remove django-allauth,
use the account remove command.

**Usage**:

```console
$ djdevx backend django packages django-allauth mfa remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-allauth oidc-provider`

Manage django-allauth with OIDC provider functionality

**Usage**:

```console
$ djdevx backend django packages django-allauth oidc-provider [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-allauth OIDC...
* `remove`: Remove OIDC provider configuration.
* `env`: Configure environment variables for OIDC...

####### `djdevx backend django packages django-allauth oidc-provider install`

Install and configure django-allauth OIDC provider.

Note: Requires django-allauth account to be installed first.
Configure environment variables using the &#x27;env&#x27; command.

**Usage**:

```console
$ djdevx backend django packages django-allauth oidc-provider install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-allauth oidc-provider remove`

Remove OIDC provider configuration.

Note: This removes OIDC configuration but keeps django-allauth
package installed. To completely remove django-allauth, use the account remove command.

**Usage**:

```console
$ djdevx backend django packages django-allauth oidc-provider remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-allauth oidc-provider env`

Configure environment variables for OIDC provider.

Auto-generates a private key for signing ID tokens.

**Usage**:

```console
$ djdevx backend django packages django-allauth oidc-provider env [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-anymail`

Manage django-anymail package

**Usage**:

```console
$ djdevx backend django packages django-anymail [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ses`: Manage django-anymail with SES backend
* `brevo`: Manage django-anymail with Brevo backend
* `mailgun`: Manage django-anymail with Mailgun backend
* `mailjet`: Manage django-anymail with Mailjet backend
* `resend`: Manage django-anymail with Resend backend

###### `djdevx backend django packages django-anymail ses`

Manage django-anymail with SES backend

**Usage**:

```console
$ djdevx backend django packages django-anymail ses [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-anymail with SES backend
* `remove`: Remove django-anymail SES backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-anymail ses install`

Install django-anymail with SES backend

**Usage**:

```console
$ djdevx backend django packages django-anymail ses install [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail ses remove`

Remove django-anymail SES backend

**Usage**:

```console
$ djdevx backend django packages django-anymail ses remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail ses env`

Configure environment variables for django-anymail SES backend

**Usage**:

```console
$ djdevx backend django packages django-anymail ses env [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-anymail brevo`

Manage django-anymail with Brevo backend

**Usage**:

```console
$ djdevx backend django packages django-anymail brevo [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-anymail with Brevo backend
* `remove`: Remove django-anymail Brevo backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-anymail brevo install`

Install django-anymail with Brevo backend

**Usage**:

```console
$ djdevx backend django packages django-anymail brevo install [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Brevo API key for authentication  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail brevo remove`

Remove django-anymail Brevo backend

**Usage**:

```console
$ djdevx backend django packages django-anymail brevo remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail brevo env`

Configure environment variables for django-anymail Brevo backend

**Usage**:

```console
$ djdevx backend django packages django-anymail brevo env [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Brevo API key for authentication  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-anymail mailgun`

Manage django-anymail with Mailgun backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailgun [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-anymail with Mailgun backend
* `remove`: Remove django-anymail Mailgun backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-anymail mailgun install`

Install django-anymail with Mailgun backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailgun install [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailgun API key for authentication  [required]
* `--domain TEXT`: The Mailgun domain  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--is-europe / --no-is-europe`: Flag to use Europe region for Mailgun  [default: no-is-europe]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail mailgun remove`

Remove django-anymail Mailgun backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailgun remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail mailgun env`

Configure environment variables for django-anymail Mailgun backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailgun env [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailgun API key for authentication  [required]
* `--domain TEXT`: The Mailgun domain  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-anymail mailjet`

Manage django-anymail with Mailjet backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailjet [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-anymail with Mailjet backend
* `remove`: Remove django-anymail Mailjet backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-anymail mailjet install`

Install django-anymail with Mailjet backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailjet install [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailjet API key for authentication  [required]
* `--secret-key TEXT`: The Mailjet Secret key for authentication  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail mailjet remove`

Remove django-anymail Mailjet backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailjet remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail mailjet env`

Configure environment variables for django-anymail Mailjet backend

**Usage**:

```console
$ djdevx backend django packages django-anymail mailjet env [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Mailjet API key for authentication  [required]
* `--secret-key TEXT`: The Mailjet Secret key for authentication  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-anymail resend`

Manage django-anymail with Resend backend

**Usage**:

```console
$ djdevx backend django packages django-anymail resend [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-anymail with Resend backend
* `remove`: Remove django-anymail Resend backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-anymail resend install`

Install django-anymail with Resend backend

**Usage**:

```console
$ djdevx backend django packages django-anymail resend install [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Resend API key for authentication  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail resend remove`

Remove django-anymail Resend backend

**Usage**:

```console
$ djdevx backend django packages django-anymail resend remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-anymail resend env`

Configure environment variables for django-anymail Resend backend

**Usage**:

```console
$ djdevx backend django packages django-anymail resend env [OPTIONS]
```

**Options**:

* `--api-key TEXT`: The Resend API key for authentication  [required]
* `--default-from-email TEXT`: The default from email address  [required]
* `--help`: Show this message and exit.

##### `djdevx backend django packages django-auditlog`

Manage django-auditlog package

**Usage**:

```console
$ djdevx backend django packages django-auditlog [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-auditlog
* `remove`: Remove django-auditlog

###### `djdevx backend django packages django-auditlog install`

Install and configure django-auditlog

**Usage**:

```console
$ djdevx backend django packages django-auditlog install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-auditlog remove`

Remove django-auditlog

**Usage**:

```console
$ djdevx backend django packages django-auditlog remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-browser-reload`

Manage django-browser-reload package

**Usage**:

```console
$ djdevx backend django packages django-browser-reload [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-browser-reload
* `remove`: Remove django-browser-reload

###### `djdevx backend django packages django-browser-reload install`

Install and configure django-browser-reload

**Usage**:

```console
$ djdevx backend django packages django-browser-reload install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-browser-reload remove`

Remove django-browser-reload

**Usage**:

```console
$ djdevx backend django packages django-browser-reload remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-cors-headers`

Manage django-cors-headers package

**Usage**:

```console
$ djdevx backend django packages django-cors-headers [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-cors-headers
* `remove`: Remove django-cors-headers package

###### `djdevx backend django packages django-cors-headers install`

Install and configure django-cors-headers

**Usage**:

```console
$ djdevx backend django packages django-cors-headers install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-cors-headers remove`

Remove django-cors-headers package

**Usage**:

```console
$ djdevx backend django packages django-cors-headers remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-csp`

Manage django-csp package

**Usage**:

```console
$ djdevx backend django packages django-csp [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-csp
* `remove`: Remove django-csp package

###### `djdevx backend django packages django-csp install`

Install and configure django-csp

**Usage**:

```console
$ djdevx backend django packages django-csp install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-csp remove`

Remove django-csp package

**Usage**:

```console
$ djdevx backend django packages django-csp remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-debug-toolbar`

Manage django-debug-toolbar package

**Usage**:

```console
$ djdevx backend django packages django-debug-toolbar [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-debug-toolbar
* `remove`: Remove django-debug-toolbar

###### `djdevx backend django packages django-debug-toolbar install`

Install and configure django-debug-toolbar

**Usage**:

```console
$ djdevx backend django packages django-debug-toolbar install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-debug-toolbar remove`

Remove django-debug-toolbar

**Usage**:

```console
$ djdevx backend django packages django-debug-toolbar remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-defender`

Manage django-defender package

**Usage**:

```console
$ djdevx backend django packages django-defender [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `env`: Creating environment variables for...
* `install`: Install and configure django-defender
* `remove`: Remove django-defender package

###### `djdevx backend django packages django-defender env`

Creating environment variables for django-defender

**Usage**:

```console
$ djdevx backend django packages django-defender env [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-defender install`

Install and configure django-defender

**Usage**:

```console
$ djdevx backend django packages django-defender install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-defender remove`

Remove django-defender package

**Usage**:

```console
$ djdevx backend django packages django-defender remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-extensions`

Manage django-extensions package

**Usage**:

```console
$ djdevx backend django packages django-extensions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-extensions
* `remove`: Remove django-extensions

###### `djdevx backend django packages django-extensions install`

Install and configure django-extensions

**Usage**:

```console
$ djdevx backend django packages django-extensions install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-extensions remove`

Remove django-extensions

**Usage**:

```console
$ djdevx backend django packages django-extensions remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-filter`

Manage django-filter package

**Usage**:

```console
$ djdevx backend django packages django-filter [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-filter
* `remove`: Remove django-filter package

###### `djdevx backend django packages django-filter install`

Install and configure django-filter

**Usage**:

```console
$ djdevx backend django packages django-filter install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-filter remove`

Remove django-filter package

**Usage**:

```console
$ djdevx backend django packages django-filter remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-guardian`

Manage django-guardian package

**Usage**:

```console
$ djdevx backend django packages django-guardian [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-guardian
* `remove`: Remove django-guardian

###### `djdevx backend django packages django-guardian install`

Install and configure django-guardian

**Usage**:

```console
$ djdevx backend django packages django-guardian install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-guardian remove`

Remove django-guardian

**Usage**:

```console
$ djdevx backend django packages django-guardian remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-health-check`

Manage django-health-check package

**Usage**:

```console
$ djdevx backend django packages django-health-check [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-health-check
* `remove`: Remove django-health-check

###### `djdevx backend django packages django-health-check install`

Install and configure django-health-check

**Usage**:

```console
$ djdevx backend django packages django-health-check install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-health-check remove`

Remove django-health-check

**Usage**:

```console
$ djdevx backend django packages django-health-check remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-meta`

Manage django-meta package

**Usage**:

```console
$ djdevx backend django packages django-meta [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-meta
* `remove`: Remove django-meta package

###### `djdevx backend django packages django-meta install`

Install and configure django-meta

**Usage**:

```console
$ djdevx backend django packages django-meta install [OPTIONS]
```

**Options**:

* `--site-protocol TEXT`: Protocol for your site URL: &#x27;http&#x27; or &#x27;https&#x27; (use https for production)  [default: https]
* `--site-domain TEXT`: Your website domain without protocol (e.g., &#x27;example.com&#x27; or &#x27;blog.example.com&#x27;)
* `--site-name TEXT`: Display name of your website (e.g., &#x27;My Awesome Blog&#x27;)
* `--site-type TEXT`: OpenGraph type (website, article, blog, product). See: https://ogp.me/#types  [default: website]
* `--use-og-properties / --no-use-og-properties`: Enable OpenGraph meta tags for rich previews on Facebook, LinkedIn, WhatsApp, etc.  [default: use-og-properties]
* `--use-twitter-properties / --no-use-twitter-properties`: Enable Twitter Card meta tags for rich previews when links are shared on Twitter/X  [default: use-twitter-properties]
* `--use-schemaorg-properties / --no-use-schemaorg-properties`: Enable Schema.org structured data for better SEO and search engine understanding  [default: use-schemaorg-properties]
* `--use-title-tag / --no-use-title-tag`: Auto-render &lt;title&gt; tags in templates (disable if you manage titles manually)  [default: use-title-tag]
* `--configure-facebook / --no-configure-facebook`: Configure Facebook-specific settings (App ID, Pages, Publisher). Info: https://developers.facebook.com/docs/sharing/webmasters  [default: no-configure-facebook]
* `--fb-app-id TEXT`: Facebook App ID from https://developers.facebook.com/apps/ (numeric ID, e.g., &#x27;123456789012345&#x27;)
* `--fb-pages TEXT`: Facebook Page ID for your business page (numeric ID, find at facebook.com/your-page/about)
* `--fb-publisher TEXT`: Full Facebook Page URL (e.g., &#x27;https://www.facebook.com/YourPageName&#x27;)
* `--configure-twitter / --no-configure-twitter`: Configure Twitter Card settings for rich previews. Guide: https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards  [default: no-configure-twitter]
* `--twitter-site TEXT`: Your website&#x27;s Twitter/X handle including @ (e.g., &#x27;@YourSite&#x27;)
* `--twitter-author TEXT`: Default author Twitter/X handle with @ (e.g., &#x27;@AuthorName&#x27;)
* `--twitter-type TEXT`: Twitter Card type: &#x27;summary&#x27; (small image) or &#x27;summary_large_image&#x27; (large image, recommended)  [default: summary_large_image]
* `--default-image-url TEXT`: Full URL to default share image (1200x630px recommended, e.g., &#x27;https://example.com/share.jpg&#x27;)
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-meta remove`

Remove django-meta package

**Usage**:

```console
$ djdevx backend django packages django-meta remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-oauth-toolkit`

Manage django-oauth-toolkit package

**Usage**:

```console
$ djdevx backend django packages django-oauth-toolkit [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-oauth-toolkit
* `remove`: Remove django-oauth-toolkit

###### `djdevx backend django packages django-oauth-toolkit install`

Install and configure django-oauth-toolkit

**Usage**:

```console
$ djdevx backend django packages django-oauth-toolkit install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-oauth-toolkit remove`

Remove django-oauth-toolkit

**Usage**:

```console
$ djdevx backend django packages django-oauth-toolkit remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-permissions-policy`

Manage django-permissions-policy package

**Usage**:

```console
$ djdevx backend django packages django-permissions-policy [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure...
* `remove`: Remove django-permissions-policy package

###### `djdevx backend django packages django-permissions-policy install`

Install and configure django-permissions-policy

**Usage**:

```console
$ djdevx backend django packages django-permissions-policy install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-permissions-policy remove`

Remove django-permissions-policy package

**Usage**:

```console
$ djdevx backend django packages django-permissions-policy remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-role-permissions`

Manage django-role-permissions package

**Usage**:

```console
$ djdevx backend django packages django-role-permissions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-role-permissions
* `remove`: Remove django-role-permissions package

###### `djdevx backend django packages django-role-permissions install`

Install and configure django-role-permissions

**Usage**:

```console
$ djdevx backend django packages django-role-permissions install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-role-permissions remove`

Remove django-role-permissions package

**Usage**:

```console
$ djdevx backend django packages django-role-permissions remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-simple-history`

Manage django-simple-history package

**Usage**:

```console
$ djdevx backend django packages django-simple-history [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-simple-history
* `remove`: Remove django-simple-history package

###### `djdevx backend django packages django-simple-history install`

Install and configure django-simple-history

**Usage**:

```console
$ djdevx backend django packages django-simple-history install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-simple-history remove`

Remove django-simple-history package

**Usage**:

```console
$ djdevx backend django packages django-simple-history remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-snakeoil`

Manage django-snakeoil package

**Usage**:

```console
$ djdevx backend django packages django-snakeoil [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-snakeoil for...
* `remove`: Remove django-snakeoil

###### `djdevx backend django packages django-snakeoil install`

Install and configure django-snakeoil for SEO metadata management

**Usage**:

```console
$ djdevx backend django packages django-snakeoil install [OPTIONS]
```

**Options**:

* `--site-name TEXT`: Display name of your website for og:site_name meta tag (e.g., &#x27;My Blog&#x27;)
* `--site-description TEXT`: Default description for your website (shown in search results and social shares)
* `--author TEXT`: Default author name for meta author tag
* `--og-type TEXT`: OpenGraph type for og:type meta tag (website, article, blog). See: https://ogp.me/#types  [default: website]
* `--default-image-url TEXT`: Full URL to default share image for social media (1200x630px recommended), or leave as default to use images/logo.svg  [default: images/logo.svg]
* `--site-url TEXT`: Your website&#x27;s full URL including protocol (e.g., &#x27;https://example.com&#x27;)
* `--locale TEXT`: Default locale/language for og:locale (e.g., &#x27;en_US&#x27;, &#x27;en_GB&#x27;, &#x27;es_ES&#x27;)
* `--twitter-site TEXT`: Twitter/X handle for your website (e.g., &#x27;@yoursite&#x27;)
* `--twitter-card-type TEXT`: Twitter card type: &#x27;summary&#x27; or &#x27;summary_large_image&#x27; (recommended for rich previews)  [default: summary_large_image]
* `--keywords TEXT`: Default keywords for SEO (comma-separated, e.g., &#x27;django, web development, python&#x27;)
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-snakeoil remove`

Remove django-snakeoil

**Usage**:

```console
$ djdevx backend django packages django-snakeoil remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-storages`

Manage django-storages package

**Usage**:

```console
$ djdevx backend django packages django-storages [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `s3`: Manage django-storages with S3 backend
* `azure`: Manage django-storages with Azure backend
* `google`: Manage django-storages with Google backend

###### `djdevx backend django packages django-storages s3`

Manage django-storages with S3 backend

**Usage**:

```console
$ djdevx backend django packages django-storages s3 [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-storages package with S3...
* `remove`: Remove django-storages S3 backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-storages s3 install`

Install django-storages package with S3 backend

**Usage**:

```console
$ djdevx backend django packages django-storages s3 install [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--bucket-name TEXT`: The AWS bucket name to store the files in  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-storages s3 remove`

Remove django-storages S3 backend

**Usage**:

```console
$ djdevx backend django packages django-storages s3 remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-storages s3 env`

Configure environment variables for django-storages S3 backend

**Usage**:

```console
$ djdevx backend django packages django-storages s3 env [OPTIONS]
```

**Options**:

* `--access-key TEXT`: The AWS access key for authentication  [required]
* `--secret-key TEXT`: The AWS Secret key for authentication  [required]
* `--region-name TEXT`: The AWS region  [required]
* `--bucket-name TEXT`: The AWS bucket name to store the files in  [required]
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-storages azure`

Manage django-storages with Azure backend

**Usage**:

```console
$ djdevx backend django packages django-storages azure [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-storages package with Azure...
* `remove`: Remove django-storages Azure backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-storages azure install`

Install django-storages package with Azure backend

**Usage**:

```console
$ djdevx backend django packages django-storages azure install [OPTIONS]
```

**Options**:

* `--account-key TEXT`: The Azure account key for authentication  [required]
* `--account-name TEXT`: The Azure account name for authentication  [required]
* `--container-name TEXT`: The Azure container name to store the files in  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-storages azure remove`

Remove django-storages Azure backend

**Usage**:

```console
$ djdevx backend django packages django-storages azure remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-storages azure env`

Configure environment variables for django-storages Azure backend

**Usage**:

```console
$ djdevx backend django packages django-storages azure env [OPTIONS]
```

**Options**:

* `--account-key TEXT`: The Azure account key for authentication  [required]
* `--account-name TEXT`: The Azure account name for authentication  [required]
* `--container-name TEXT`: The Azure container name to store the files in  [required]
* `--help`: Show this message and exit.

###### `djdevx backend django packages django-storages google`

Manage django-storages with Google backend

**Usage**:

```console
$ djdevx backend django packages django-storages google [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install django-storages package with...
* `remove`: Remove django-storages Google backend
* `env`: Configure environment variables for...

####### `djdevx backend django packages django-storages google install`

Install django-storages package with Google backend

**Usage**:

```console
$ djdevx backend django packages django-storages google install [OPTIONS]
```

**Options**:

* `--credentials-file-path PATH`: The path to the google credential file  [required]
* `--bucket-name TEXT`: The Google bucket name to store the files in  [required]
* `--help`: Show this message and exit.

####### `djdevx backend django packages django-storages google remove`

Remove django-storages Google backend

**Usage**:

```console
$ djdevx backend django packages django-storages google remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django packages django-storages google env`

Configure environment variables for django-storages Google backend

**Usage**:

```console
$ djdevx backend django packages django-storages google env [OPTIONS]
```

**Options**:

* `--credentials-file-path PATH`: The path to the google credential file  [required]
* `--bucket-name TEXT`: The Google bucket name to store the files in  [required]
* `--help`: Show this message and exit.

##### `djdevx backend django packages django-taggit`

Manage django-taggit package

**Usage**:

```console
$ djdevx backend django packages django-taggit [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-taggit
* `remove`: Remove django-taggit

###### `djdevx backend django packages django-taggit install`

Install and configure django-taggit

**Usage**:

```console
$ djdevx backend django packages django-taggit install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-taggit remove`

Remove django-taggit

**Usage**:

```console
$ djdevx backend django packages django-taggit remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages django-tailwind-cli`

Manage django-tailwind-cli package

**Usage**:

```console
$ djdevx backend django packages django-tailwind-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure django-tailwind-cli
* `remove`: Remove django-tailwind-cli

###### `djdevx backend django packages django-tailwind-cli install`

Install and configure django-tailwind-cli

**Usage**:

```console
$ djdevx backend django packages django-tailwind-cli install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages django-tailwind-cli remove`

Remove django-tailwind-cli

**Usage**:

```console
$ djdevx backend django packages django-tailwind-cli remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages heroicons`

Manage heroicons package

**Usage**:

```console
$ djdevx backend django packages heroicons [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure heroicons
* `remove`: Remove heroicons

###### `djdevx backend django packages heroicons install`

Install and configure heroicons

**Usage**:

```console
$ djdevx backend django packages heroicons install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages heroicons remove`

Remove heroicons

**Usage**:

```console
$ djdevx backend django packages heroicons remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages djangochannelsrestframework`

Manage djangochannelsrestframework package

**Usage**:

```console
$ djdevx backend django packages djangochannelsrestframework [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure...
* `remove`: Remove djangochannelsrestframework package

###### `djdevx backend django packages djangochannelsrestframework install`

Install and configure djangochannelsrestframework

**Usage**:

```console
$ djdevx backend django packages djangochannelsrestframework install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages djangochannelsrestframework remove`

Remove djangochannelsrestframework package

**Usage**:

```console
$ djdevx backend django packages djangochannelsrestframework remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages djangorestframework`

Manage djangorestframework package

**Usage**:

```console
$ djdevx backend django packages djangorestframework [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure djangorestframework
* `remove`: Remove djangorestframework

###### `djdevx backend django packages djangorestframework install`

Install and configure djangorestframework

**Usage**:

```console
$ djdevx backend django packages djangorestframework install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages djangorestframework remove`

Remove djangorestframework

**Usage**:

```console
$ djdevx backend django packages djangorestframework remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages drf-nested-routers`

Manage drf-nested-routers package

**Usage**:

```console
$ djdevx backend django packages drf-nested-routers [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure drf-nested-routers
* `remove`: Remove drf-nested-routers package

###### `djdevx backend django packages drf-nested-routers install`

Install and configure drf-nested-routers

**Usage**:

```console
$ djdevx backend django packages drf-nested-routers install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages drf-nested-routers remove`

Remove drf-nested-routers package

**Usage**:

```console
$ djdevx backend django packages drf-nested-routers remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages drf-flex-fields`

Manage drf-flex-fields package

**Usage**:

```console
$ djdevx backend django packages drf-flex-fields [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure drf-flex-fields
* `remove`: Remove drf-flex-fields package

###### `djdevx backend django packages drf-flex-fields install`

Install and configure drf-flex-fields

**Usage**:

```console
$ djdevx backend django packages drf-flex-fields install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages drf-flex-fields remove`

Remove drf-flex-fields package

**Usage**:

```console
$ djdevx backend django packages drf-flex-fields remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages drf-spectacular`

Manage drf-spectacular package

**Usage**:

```console
$ djdevx backend django packages drf-spectacular [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure drf-spectacular
* `remove`: Remove drf-spectacular package

###### `djdevx backend django packages drf-spectacular install`

Install and configure drf-spectacular

**Usage**:

```console
$ djdevx backend django packages drf-spectacular install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages drf-spectacular remove`

Remove drf-spectacular package

**Usage**:

```console
$ djdevx backend django packages drf-spectacular remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django packages whitenoise`

Manage whitenoise package

**Usage**:

```console
$ djdevx backend django packages whitenoise [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install and configure whitenoise
* `remove`: Remove whitenoise

###### `djdevx backend django packages whitenoise install`

Install and configure whitenoise

**Usage**:

```console
$ djdevx backend django packages whitenoise install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django packages whitenoise remove`

Remove whitenoise

**Usage**:

```console
$ djdevx backend django packages whitenoise remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx backend django feature`

Add features to your Django project

**Usage**:

```console
$ djdevx backend django feature [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pwa`: Add PWA support to the project
* `css`: Manage css frameworks
* `tailwind-theme`: Manage tailwind theme
* `tailwind-ui`: Manage tailwind ui

##### `djdevx backend django feature pwa`

Add PWA support to the project

**Usage**:

```console
$ djdevx backend django feature pwa [OPTIONS]
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

##### `djdevx backend django feature css`

Manage css frameworks

**Usage**:

```console
$ djdevx backend django feature css [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `bootstrap`: Manage bootstrap css framework
* `frankenui`: Manage Franken UI css framework
* `semantic`: Manage Semantic css framework

###### `djdevx backend django feature css bootstrap`

Manage bootstrap css framework

**Usage**:

```console
$ djdevx backend django feature css bootstrap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Add Bootstrap CSS framework to the project.
* `remove`: Remove Bootstrap CSS framework from the...

####### `djdevx backend django feature css bootstrap install`

Add Bootstrap CSS framework to the project.

Downloads the specified version (or latest) of Bootstrap&#x27;s minified CSS, theme CSS,
JavaScript files, and jQuery, then saves them to the static directory.

**Usage**:

```console
$ djdevx backend django feature css bootstrap install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django feature css bootstrap remove`

Remove Bootstrap CSS framework from the project.

**Usage**:

```console
$ djdevx backend django feature css bootstrap remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django feature css frankenui`

Manage Franken UI css framework

**Usage**:

```console
$ djdevx backend django feature css frankenui [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Add FrankenUI CSS framework to the project.
* `remove`: Remove FrankenUI CSS framework from the...

####### `djdevx backend django feature css frankenui install`

Add FrankenUI CSS framework to the project.

Downloads the specified version (or latest) of FrankenUI&#x27;s minified CSS
and JavaScript files, then saves them to the static directory.

**Usage**:

```console
$ djdevx backend django feature css frankenui install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django feature css frankenui remove`

Remove FrankenUI CSS framework from the project.

**Usage**:

```console
$ djdevx backend django feature css frankenui remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django feature css semantic`

Manage Semantic css framework

**Usage**:

```console
$ djdevx backend django feature css semantic [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Add Semantic UI CSS framework to the project.
* `remove`: Remove Semantic css framework from the...

####### `djdevx backend django feature css semantic install`

Add Semantic UI CSS framework to the project.

Downloads the latest Semantic UI (from jsdelivr tags) and jQuery, saves them to the
static directory, and updates the base template to include links.

**Usage**:

```console
$ djdevx backend django feature css semantic install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

####### `djdevx backend django feature css semantic remove`

Remove Semantic css framework from the project.

**Usage**:

```console
$ djdevx backend django feature css semantic remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django feature tailwind-theme`

Manage tailwind theme

**Usage**:

```console
$ djdevx backend django feature tailwind-theme [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install Tailwind theme with customizable...
* `remove`: Remove Tailwind theme.

###### `djdevx backend django feature tailwind-theme install`

Install Tailwind theme with customizable colors.

**Usage**:

```console
$ djdevx backend django feature tailwind-theme install [OPTIONS]
```

**Options**:

* `--primary-color TEXT`: Primary color (hex code or CSS variable). Example: #0047AB or --color-blue-500  [default: #0047AB]
* `--secondary-color TEXT`: Secondary color (hex code or CSS variable). Example: #2F739F or --color-slate-600  [default: #2F739F]
* `--accent-color TEXT`: Accent color (hex code or CSS variable). Example: #F38B49 or --color-orange-500  [default: #F38B49]
* `--neutral-color TEXT`: Neutral color (hex code or CSS variable). Example: #728389 or --color-zinc-500  [default: #728389]
* `--bg-light TEXT`: Background color for light theme (hex code or CSS variable). Example: #FFFFFF or --color-white  [default: #FFFFFF]
* `--bg-secondary-light TEXT`: Secondary background color for light theme (hex code or CSS variable). Example: #84A8E0 or --color-primary-200  [default: #FBFBFB]
* `--bg-tertiary-light TEXT`: Tertiary background color for light theme (hex code or CSS variable). Example: #C8DFE9 or --color-secondary-200  [default: #F8FFFF]
* `--text-light TEXT`: Text color for light theme (hex code or CSS variable). Example: #0f172a or --color-slate-900  [default: --color-slate-900]
* `--text-secondary-light TEXT`: Secondary text color for light theme (hex code or CSS variable). Example: #334155 or --color-slate-700  [default: --color-slate-700]
* `--text-muted-light TEXT`: Muted text color for light theme (hex code or CSS variable). Example: #64748b or --color-slate-500  [default: --color-slate-500]
* `--bg-dark TEXT`: Background color for dark theme (hex code or CSS variable). Example: #0A0F1A  [default: #0A0F1A]
* `--bg-secondary-dark TEXT`: Secondary background color for dark theme (hex code or CSS variable). Example: #132035  [default: #132035]
* `--bg-tertiary-dark TEXT`: Tertiary background color for dark theme (hex code or CSS variable). Example: #182945  [default: #182945]
* `--text-dark TEXT`: Text color for dark theme (hex code or CSS variable). Example: #f1f5f9 or --color-slate-100  [default: --color-slate-100]
* `--text-secondary-dark TEXT`: Secondary text color for dark theme (hex code or CSS variable). Example: #cbd5e1 or --color-slate-300  [default: --color-slate-300]
* `--text-muted-dark TEXT`: Muted text color for dark theme (hex code or CSS variable). Example: #64748b or --color-slate-500  [default: --color-slate-500]
* `--help`: Show this message and exit.

###### `djdevx backend django feature tailwind-theme remove`

Remove Tailwind theme.

**Usage**:

```console
$ djdevx backend django feature tailwind-theme remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `djdevx backend django feature tailwind-ui`

Manage tailwind ui

**Usage**:

```console
$ djdevx backend django feature tailwind-ui [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install Tailwind UI
* `remove`: Remove Tailwind UI.

###### `djdevx backend django feature tailwind-ui install`

Install Tailwind UI

**Usage**:

```console
$ djdevx backend django feature tailwind-ui install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

###### `djdevx backend django feature tailwind-ui remove`

Remove Tailwind UI.

**Usage**:

```console
$ djdevx backend django feature tailwind-ui remove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `djdevx backend django create`

Create new Django applications or components

**Usage**:

```console
$ djdevx backend django create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `app`: Create a new Django application
* `admin`: Create admin.py from model.py for an...

##### `djdevx backend django create app`

Create a new Django application

**Usage**:

```console
$ djdevx backend django create app [OPTIONS]
```

**Options**:

* `--application-name TEXT`: Application name
* `--help`: Show this message and exit.

##### `djdevx backend django create admin`

Create admin.py from model.py for an application

**Usage**:

```console
$ djdevx backend django create admin [OPTIONS]
```

**Options**:

* `--application-name TEXT`: Application name
* `--help`: Show this message and exit.
