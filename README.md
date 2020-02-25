# SFDS Email microservice.py [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/email-microservice-py/master)](https://circleci.com/gh/SFDigitalServices/email-microservice-py)
SFDS Email microservice is a service intended for developers inside the city to send emails on a standard transactional email service platform such as Sendgrid, Mailgun, Amaozon SES ... etc. Only Sendgrid is supported at this time; other email service implementation is not on the road map.

## Extension and Development
This project is forked from [SFDS microservice boilerplate](https://github.com/SFDigitalServices/microservice-py). If you wish to extend other email service providers, please follow the instructions on the SFDS microservice boilerplate repo. If you find this project useful, you may use the code here.

## Get started
*** You must have a APIGee API key to continue. To obtain a key, please contact SF Digital Services.

A sample POST data is provided in ``` data-sample.json ``` and ``` data-full.json ```, you will be responsible to complete the values in brackets([]) before using the service.

Terminal command with curl:
```
curl --location --request POST 'https://sfds-dev.apigee.net/emailservice' \
--header 'x-apikey: [INSERT YOUR APIGEE API KEY HERE]' \
--header 'Content-Type: text/plain' \
-d @data-sample.json
```

If the command is successful, you will receive an email in your inbox; otherwise an error message is returned to your console.

For detail of the fields in the json data, please see below.

## Field properties
The json data follows [Sendgrid's sendmail API](https://sendgrid.com/docs/api-reference/) specs with the following changes:

- `ip_pool_name` is ommitted.
- `to` is added to the top level. If `personalization` is not used, this will be set as the mail to field.
- `attachments`
    - `path` is added for files hosted externally
    - `content_id` is ommitted
    - `disposition` is ommitted
- `dynamic_template_data` is added to the top leve. If `template_id` is specified, the key/value pair will be mapped in the template.
    See [Dynamic Template Data](https://sendgrid.com/docs/ui/sending-email/how-to-send-an-email-with-dynamic-transactional-templates/) for more details.
