# OrangeHRM Playwright Automation

[![GitHub Actions](https://github.com/mudassarns/orangehrm_playwright_project/actions/workflows/pytest.yml/badge.svg?branch=dev)](https://github.com/mudassarns/orangehrm_playwright_project/actions/workflows/pytest.yml)

A Python test-automation portfolio demonstrating browser, REST API, database, email, and cross-layer testing against OrangeHRM using Playwright and pytest.

## What this project demonstrates

- Browser automation with Playwright and reusable page objects.
- REST API validation and JSON Schema response checks.
- MariaDB verification for employee records and persistence.
- Hybrid workflows combining UI, API, and database checks.
- Reusable authentication state and pytest fixtures for employee creation and cleanup.
- Gmail email verification using SMTP and read-only Gmail API access.
- Parallel pytest execution, HTML reporting, GitHub Actions, and Buildkite configuration.

## Technology stack

Python 3.14 · Playwright · pytest · Requests/Playwright APIRequestContext · MariaDB · Docker Compose · JSON Schema · Gmail API · Gmail SMTP · GitHub Actions · Buildkite

## Project structure

```text
api/                 OrangeHRM API client
db/                  MariaDB client
docker-orangehrm/    Docker Compose configuration
email_service/       Gmail sender and OAuth reader
pages/               Playwright page objects
schemas/             API response schemas
tests/               UI, API, database, email, and hybrid tests
utils/               Test-data and screenshot utilities
conftest.py          Shared authentication, API, DB, and cleanup fixtures
config.py            Environment-based configuration
pytest.ini           Pytest markers, retries, and HTML reporting
requirements.txt     Python dependencies
.env.example         Safe local configuration template
.github/workflows/   GitHub Actions workflow
.buildkite/          Buildkite pipeline definition
```

## Test coverage

| Module | Purpose |
|---|---|
| `tests/test_ui.py` | Playwright browser workflows |
| `tests/test_api.py` | Employee API operations and response validation |
| `tests/test_database.py` | Employee database and persistence checks |
| `tests/test_email.py` | Email delivery and Gmail API verification |
| `tests/test_hybrid.py` | Cross-layer UI/API/database workflows |

Employee-creation fixtures include cleanup logic. Tests that use Gmail require a separately configured Gmail sender and OAuth reader; they are not a prerequisite for understanding or running the UI/API portions.

## Prerequisites

- Python 3.14
- Docker Desktop with Docker Compose
- Git
- A local OrangeHRM and MariaDB environment
- A Gmail account with an app password and OAuth client setup only if running email-verification tests

## Local setup (PowerShell)

Run commands from the repository root.

1. Create and activate a virtual environment:

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies and Playwright Chromium:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python -m playwright install --with-deps chromium
   Copy-Item .env.example .env
   ```

3. Edit `.env` and replace the local database and OrangeHRM credential placeholders. Keep the MariaDB password values consistent with the local container and installation. The template leaves `MARIADB_DATABASE` empty to match the existing Compose/installer flow.

4. Start the containers and verify their status:

   ```powershell
   docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d --wait
   docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps
   ```

5. On a fresh database, install OrangeHRM before testing. The GitHub Actions workflow's **Install OrangeHRM via official CLI installer** step documents the automated installer flow. Configure it for local use with your local database and administrator values; the CI workflow itself is not a local setup script.

6. Confirm OrangeHRM is accessible at `http://localhost:8080`, then run tests.

## Running tests

Run the full suite:

```powershell
pytest -v
```

Run individual modules:

```powershell
pytest tests/test_ui.py -v
pytest tests/test_api.py -v
pytest tests/test_database.py -v
pytest tests/test_hybrid.py -v
pytest tests/test_email.py -v
```

Run tests in parallel:

```powershell
pytest -n 4 -v
```

The configured HTML report is written to `reports/test-report.html`. The `--env` option selects an environment prefix; the default is `qa`, so configuration values use the `QA_` prefix.

## Environment configuration

Copy `.env.example` to `.env`. Set the local OrangeHRM URL and credentials, database connection details, and MariaDB container initialization values.

Gmail is optional for the UI/API-only test groups. To run email tests, configure:

- `QA_GMAIL_ADDRESS` and `QA_GMAIL_APP_PASSWORD` for sending mail through SMTP.
- `QA_GMAIL_OAUTH_CLIENT_FILE` and `QA_GMAIL_TOKEN_FILE` with paths to local OAuth client and token JSON files.

Google OAuth client and token files must be obtained through your own Google Cloud project and authorization flow. They are not included in this repository.

## Gmail verification and token recovery

The email test sends a uniquely identified message through SMTP and verifies it using read-only Gmail API access.

If Gmail API authentication fails because the refresh token is revoked or expired:

1. Keep the OAuth client file; remove or rename only the local token file.
2. Run `pytest tests/test_email.py -q` and complete Google authorization when prompted.
3. Confirm the test passes and a new token file is written to the path configured by `QA_GMAIL_TOKEN_FILE`.
4. If CI requires Gmail verification, update the GitHub Actions secret `QA_GMAIL_TOKEN_JSON` with the newly authorized token JSON using the repository's existing secret-management process.

The workflow uses `QA_GMAIL_OAUTH_CLIENT_JSON` and `QA_GMAIL_TOKEN_JSON` secrets to provision OAuth files in CI. OAuth refresh tokens issued to an external OAuth app in Testing status may expire after seven days for Gmail scopes. See [Google OAuth refresh-token expiration](https://developers.google.com/identity/protocols/oauth2#expiration).

Never commit or publish OAuth client JSON, token JSON, Gmail app passwords, or database/application credentials.

## CI

The GitHub Actions workflow runs on pushes to `dev`. It installs Python dependencies and Playwright browsers, starts and initializes the Docker stack, runs the test suite in parallel, uploads the HTML report, and tears down the stack. CI credentials are supplied through GitHub Actions Secrets, not from a developer's local `.env`.

Buildkite configuration is maintained in `.buildkite/pipeline.yml`.

## Security

- Keep `.env`, `.env.*`, OAuth client/token JSON files, private keys, and local test artifacts out of Git.
- Store CI credentials in GitHub Actions Secrets.
- Never print or publish credential or token contents.
- Use a disposable local/test environment for tests that create or delete employee records.

## Related projects

- [OrangeHRM Selenium Automation](https://github.com/mudassarns/orangehrm_pytest_project)
- [OrangeHRM AI SDET Project](https://github.com/mudassarns/orangehrm_ai_sdet_project)
