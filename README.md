# OrangeHRM Playwright Automation

Python-based test automation for OrangeHRM using Playwright, pytest, API validation, MariaDB verification, and Gmail integration.

## Tech Stack

- Python 3.14
- Playwright and pytest
- OrangeHRM 5.9 running in Docker
- MariaDB for database validation
- JSON Schema for API response validation
- Gmail SMTP and Gmail API for email verification
- GitHub Actions and Buildkite for CI

## Project Structure

```text
api/                 OrangeHRM API client
db/                  MariaDB client
docker-orangehrm/    Docker Compose configuration
email_service/       Gmail sender and OAuth reader
pages/               Playwright page objects
schemas/             API response schemas
tests/               UI, API, DB, email and hybrid tests
utils/               Test data and screenshot utilities
conftest.py           Shared pytest fixtures
config.py             Environment-based configuration
pytest.ini            Pytest settings and reporting
```

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   python -m playwright install
   ```

3. Configure the required `QA_` environment variables in the root `.env`. These include OrangeHRM URL and credentials, database connection details, Gmail address and app password, OAuth client file path, and token file path.

4. Start OrangeHRM and MariaDB:

   ```powershell
   docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d --wait
   ```

5. Ensure OrangeHRM is installed and accessible at `http://localhost:8080`.

## Running Tests

Run the full suite:

```powershell
pytest -v
```

Run individual test groups:

```powershell
pytest tests/test_ui.py -v
pytest tests/test_api.py -v
pytest tests/test_database.py -v
pytest tests/test_email.py -v
pytest tests/test_hybrid.py -v
```

The configured pytest report is written to `reports/test-report.html`. Tests use shared fixtures for authentication, employee creation and cleanup, API access, and database connections.

## Gmail OAuth Token Recovery

The Gmail verification test sends a uniquely identified email using SMTP, then verifies the received message through the Gmail API with read-only OAuth access.

If the test fails with `invalid_grant` or a revoked/expired refresh token:

1. Delete or rename the existing local `gmail_token.json`. Keep `gmail_oauth_client.json`; it is needed for authorization.
2. Run:

   ```powershell
   pytest tests/test_email.py -q
   ```

3. Complete Google authorization in the browser when prompted. Confirm the test passes and a new token file is generated at the path configured by `QA_GMAIL_TOKEN_FILE`.
4. On GitHub, open **Settings → Secrets and variables → Actions**.
5. Replace `QA_GMAIL_TOKEN_JSON` with the complete contents of the new token JSON file.
6. Rerun the failed workflow and verify that the email test passes.

The GitHub Actions workflow supplies the OAuth client configuration and token through `QA_GMAIL_OAUTH_CLIENT_JSON` and `QA_GMAIL_TOKEN_JSON`.

**Important:** OAuth applications in external Testing mode generally issue refresh tokens that expire after seven days when requesting Gmail read-only access. If the app remains in Testing, token recovery may need to be repeated. See [Google OAuth refresh-token expiration](https://developers.google.com/identity/protocols/oauth2#expiration).

Never commit, publish, or share token JSON, OAuth client secrets, Gmail app passwords, or database/application credentials.

## CI

GitHub Actions runs on pushes to `dev`. It installs dependencies and browsers, starts Docker, installs and verifies OrangeHRM, runs the test suite in parallel, uploads the HTML report, and tears down the Docker stack.

Buildkite configuration is maintained in `.buildkite/pipeline.yml`.

CI credentials are supplied through GitHub Actions Secrets; local `.env` values are not automatically available to CI.

## Security

Keep `.env`, `gmail_token.json`, `gmail_token_old.json`, and `gmail_oauth_client.json` out of Git. Store CI credentials in GitHub Actions Secrets. Do not print credentials or token contents in logs.
