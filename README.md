# `djdevx`

## Supercharge Your Django Development Workflow

`djdevx` is a powerful command-line tool designed to enhance the productivity and experience of Django developers. `djdevx` provides a suite of features to streamline your workflow and make development enjoyable.

### Key Features

- **Simplified Project Setup**: Quickly scaffold Django applications with best practices.
- **Enhanced Debugging Tools**: Integrate popular debugging packages effortlessly.
- **Customizable Templates**: Leverage pre-configured templates for common Django use cases.
- **Optimized Developer Experience**: Automate repetitive tasks and focus on writing great code.

### Why Choose `djdevx`?

- **Comprehensive Command Suite**: From initializing projects to managing packages and adding features, `djdevx` provides a wide range of commands to simplify Django development.
- **Devcontainer Support**: Pre-configured `.devcontainer` setup for Visual Studio Code, including Docker Compose integration and essential extensions for Django development.
- **Devbox Integration**: Ready-to-use `devbox.json` and `.env` templates for creating consistent and portable development environments.
- **Pre-commit Hooks**: Includes a robust `.pre-commit-config.yaml` with hooks for linting, formatting, and code quality checks.
- **Docker Support**: Provides `Dockerfile` for containerized development and deployment.
- **Environment Variable Management**: Templates for `.env` files to simplify environment-specific configurations.
- **Package Management**: Easily install and configure popular Django packages like `django-allauth`, `django-debug-toolbar`, `djangorestframework`, and more.
- **Feature Addition**: Quickly add features like PWA support, deployment configurations, and custom app scaffolding.
- **Time-Efficient**: Streamline repetitive tasks and minimize setup time.

Explore the full list of commands and features in the [Manual](manual.md) to see how `djdevx` can enhance your Django development experience.

### Getting Started

1. Install `djdevx` using pip:
   ```bash
   uv tool install git+https://github.com/siavashoutadi/djdevx
   ```
2. Initialize a new Django project:
   ```bash
   ddx init
   ```
3. Install and configure a package, for example, `whitenoise`:
   ```bash
   ddx packages whitenoise install
   ```
4. Explore the available commands:
   ```bash
   ddx --help
   ```

### License

`djdevx` is open-source software licensed under the [MIT License](LICENSE).

---

Boost your Django development experience with `djdevx` today!
