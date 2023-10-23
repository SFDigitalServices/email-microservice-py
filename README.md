# Email Microservice

[![SFDigitalServices](https://circleci.com/gh/SFDigitalServices/email-microservice-py.svg?style=svg)](https://circleci.com/gh/SFDigitalServices/email-microservice-py)

The Email microservice is a supports automated processes within the City & County of San Francisco to send templated emails via [SendGrid]. <!-- Other email service implementations (Mailgun, Amazon SES, etc.) are not yet supported. -->

## Get started

### First Time Setup

#### Databases

Install Postgres (if needed)

```bash
brew install postgresql
```

Create database

```bash
createdb email_microservice
```

Install Redis (if needed)

```bash
brew install redis
```

Create a local config (by copying)

```bash
cp .env.example .env
```

Edit the following line

```bash
export REDIS_URL=redis://localhost:6379
```

Start the databases

```bash
brew services start postgresql@14
brew services start redis
```

If you want to verify the services running, you can use

```bash
brew services list
```

#### Environment and Dependencies

Install Pipenv (if needed)

```bash
pip install --user pipenv
```

Install packages

```bash
pipenv install --dev
```

Note: if you have (mini)Conda installed, you might have to adjust the Python
executable. If so, you can run something like this ([see for more info](https://stackoverflow.com/questions/50546339/pipenv-with-conda)):

```bash
pipenv --python=$(conda run which python) --site-packages
```

Migrate DB

```bash
pipenv run alembic upgrade head
```

### Run the server

```bash
ACCESS_KEY=123456 pipenv run gunicorn --reload 'service.microservice:start_service()' --timeout 600
```

Start celery worker

```bash
pipenv run celery worker
```

## API

All API endpoints must be called via HTTP `POST` with a JSON request body and the following headers:

* `ACCESS_KEY`: Your API access key
* `Content-Type`: `application/json`

### Send an email with template

```json
{
  "subject": "Hi Diddly Ho",
  "to": [{
    "email": "homer@springfield.com",
    "name": "Homer Simpson"
  }],
  "from": {
    "email": "ned@flandersfamily.com",
    "name": "Ned Flanders"
    "template": {
      "url": "https://static.file.com/template.html",
      "replacements" {
        "var1": "hello!",
        "var2": {
          "first_name": "homer",
          "last_name": "simpson"
        }
      }
    }
  }
}
```

### Attachments

You can provide attachments either inline (with the base64-encoded `content` field) or via URL in the `path` field. You may also provide request `headers` for URL attachments that require additional authentication.

```json
{
  "subject": "Status Report",
  "to": [{
    "email": "cburns@springfieldnuclear.com",
    "name": "Charles Burns"
  }],
  "from": {
    "email": "wsmithers@springfieldnuclear.com",
    "name": "Waylon Smithers"
  },
  "content": {
    "type": "text/plain",
    "value": "All systems are in operating condition."
  },
  "attachments": [
    {
      "content": "YmFzZTY0IHN0cmluZw==",
      "filename": "report.txt",
      "type": "text/plain"
    },
    {
      "filename": "report.pdf",
      "path": "https://www.springfieldnuclear.com/report.pdf",
      "type": "application/pdf",
      "headers": {
          "api-key": "123ABC"
      }
    }
  ]
}
```

### Filter: clicktrack

[docs.sendgrid.com](https://docs.sendgrid.com/for-developers/sending-email/smtp-filters#filter-clicktrack)

```json
{
  "subject": "Hi Diddly Ho",
  "to": [{
    "email": "homer@springfield.com",
    "name": "Homer Simpson"
  }],
  "from": {
    "email": "ned@flandersfamily.com",
    "name": "Ned Flanders"
  },
  "content": [
    {
      "type": "text/plain",
      "value": "Try search with https://google.com"
    }
  ],
  "filters" : {
    "clicktrack" : {
      "settings" : {
        "enable" : 0,
        "enable_text" : false
      }
    }
  }
}
```

## Testing

Code coverage command with missing statement line numbers

```bash
pipenv run python -m pytest -s --cov=service --cov=tasks tests/ --cov-report term-missing
```

## Revising the database

Create a migration

```bash
pipenv run alembic revision -m "Add a column"
```

Edit the created revision file to add the steps to implement and rollback
the changes you want to make.

Run DB migrations

```bash
pipenv run alembic upgrade head
```

## Templating

Templates are rendered with [Jinja].

[jinja]: (https://jinja.palletsprojects.com/en/3.1.x/templates/)
[sendgrid]: https://docs.sendgrid.com/for-developers
