# SFDS Email Microservice [![SFDigitalServices](https://circleci.com/gh/SFDigitalServices/email-microservice-py.svg?style=svg)](https://circleci.com/gh/SFDigitalServices/email-microservice-py)

SFDS Email microservice is a service intended for developers inside the city to send emails on a standard transactional email service platform such as Sendgrid, Mailgun, Amaozon SES ... etc. Only Sendgrid is supported at this time; other email service implementation is not on the road map.

## Get started

### Run the server

```
ACCESS_KEY=123456 pipenv run gunicorn --reload 'service.microservice:start_service()' --timeout 600
```

Start celery worker

```
pipenv run celery worker
```

## API

### send an email with template

```
post /email
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
```

### send an email with 2 different methods of file attachments

```
post /email
{
    "subject": "Status Report",
    "to": [{
        "email": "cburns@springfieldnuclear.com",
        "name": "Charles Burns"
    }],
    "from": {
        "email": "wsmithers@springfieldnuclear.com",
        "name": "Waylon Smithers"
    "content": {
        "type": "text/plain",
        "value": "All systems are in operating condition."
    },
    "attachments": [{
        "content": "YmFzZTY0IHN0cmluZw==",
        "filename": "report.txt",
        "type": "text/plain"
    },{
        "filename": "report.pdf",
        "path": "https://www.springfieldnuclear.com/report.pdf",
        "type": "application/pdf",
        "headers": {
            "api-key": "123ABC"
        }
    }]
}
```

## Testing

Code coverage command with missing statement line numbers

```
pipenv run python -m pytest -s --cov=service --cov=tasks tests/ --cov-report term-missing
```

## Revising the database

Create a migration

```
pipenv run alembic revision -m "Add a column"
```

Edit the created revision file to add the steps to implement and rollback
the changes you want to make.

Run DB migrations

```
pipenv run alembic upgrade head
```

## Templating

Templates are rendered with [Jinja](https://jinja.palletsprojects.com/en/3.1.x/templates/).
