# SFDS Email microservice.py [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/email-microservice-py/master)](https://circleci.com/gh/SFDigitalServices/email-microservice-py)
SFDS Email microservice is a service intended for developers inside the city to send emails on a standard transactional email service platform such as Sendgrid, Mailgun, Amaozon SES ... etc. Only Sendgrid is supported at this time; other email service implementation is not on the road map.

## Extension and Development
This project is forked from [SFDS microservice boilerplate](https://github.com/SFDigitalServices/microservice-py). If you wish to extend other email service providers, please follow the instructions on the SFDS microservice boilerplate repo. If you find this project useful, you may use the code here.

## Get started
*** You must have a APIGee API key to continue. To obtain a key, please contact SF Digital Services.

A sample POST data is provided in ``` data-sample.json ``` and ``` data-full.json ```, you will be responsible to complete the values in brackets([]) before using the service.

Terminal command with curl:
```
curl --location --request POST 'http://127.0.0.1:8000/email' \
--header 'x-apikey: [INSERT YOUR APIGEE API KEY HERE]' \
--header 'Content-Type: text/plain' \
-d @data-sample.json
```

If the command is successful, you will receive an email in your inbox; otherwise an error message is returned to your console.

For detail of the fields in the json data, please see below.

## Field properties
| Property&nbsp;name   | Description                                                                           |  | | Required|
|----------|---------------------------------------------------------------------------------------|-----------------------| ------ | -----|
| SENDGRID_API_KEY | Your Sendgrid API Key | | | | required|
| asm | An object allowing you to specify how to handle unsubscribes.| | | |optional|
&nbsp;|group_id | The unsubscribe group to associate with this email| | required |
&nbsp;|groups_to_display | An array containing the unsubscribe groups that you would like to be displayed on the unsubscribe preferences page.| |  optional |
| attachments |An array of objects in which you can specify any attachments you want to include | | | optional|
&nbsp;|content | The Base64 encoded content of the attachment.| | optional |
&nbsp;|filename | The filename of the attachment.| | required |
&nbsp;|path | If file content is missing, specify the url to the file online | | optional |
&nbsp;|type | The mime type of the content you are attaching. For example, “text/plain” or “text/html”.| | optional |
| batch_id | This ID represents a batch of emails to be sent at the same time. Including a batch_id in your request allows you include this email in that batch, and also enables you to cancel or pause the delivery of that batch. For more information, see https://sendgrid.com/docs/API_Reference/Web_API_v3/cancel_schedule_send | | optional|
| categories | An array of category names for this message. Each category name may not exceed 255 characters. | ||optional |
| content | An array in which you may specify the content of your email. You can include multiple mime types of content, but you must specify at least one mime type. To include more than one mime type, simply add another object to the array containing the type and value parameters. ||| required |
&nbsp;|type | The mime type of the content you are including in your email. For example, “text/plain” or “text/html”.| |required |
&nbsp;| value| The actual content of the specified mime type that you are including in your email. | |required |
| custom_args| Values that are specific to the entire send that will be carried along with the email and its activity data. Key/value pairs must be strings. Substitutions will not be made on custom arguments, so any string that is entered into this parameter will be assumed to be the custom argument that you would like to be used. This parameter is overridden by personalizations[x].custom_args if that parameter has been defined. Total custom args size may not exceed 10,000 bytes | ||optional |
| to | An array of recipients. Each object within this array may contain the name, but must always contain the email, of a recipient.| ||required |
&nbsp;|email | Email || required |
&nbsp;|name | The name of the person or company that is sending the email.|| optional|
| from | ||| required |
|&nbsp;email | Email || required |
&nbsp;|name | The name of the person or company that is sending the email.| |optional|
| headers | An object containing key/value pairs of header names and the value to substitute for them. The Key/value pairs must be strings. You must ensure these are properly encoded if they contain unicode characters. Must not be one of the reserved headers.| || optional |
| mail_settings | A collection of different mail settings that you can use to specify how you would like this email to be handled.| ||optional |
&nbsp;|bcc | This allows you to have a blind carbon copy automatically sent to the specified email address for every email that is sent.| |optional |
&nbsp; &nbsp;|email | The email address that you would like to receive the BCC. |optional |
&nbsp; &nbsp;|enable | Indicates if this setting is enabled.| optional |
&nbsp;|bypass_list_management | Allows you to bypass all unsubscribe groups and suppressions to ensure that the email is delivered to every single recipient. This should only be used in emergencies when it is absolutely necessary that every recipient receives your email.| |optional |
&nbsp;&nbsp;| enable | Indicates if this setting is enabled.| optional |
&nbsp;|footer | The default footer that you would like included on every email.|| optional |
&nbsp;&nbsp;| enable | Indicates if this setting is enabled.| optional |
&nbsp;&nbsp;| html| The HTML content of your footer.| optional |
&nbsp;&nbsp;| text | The text content of your footer.| optional |
&nbsp;|sandbox_mode | This allows you to send a test email to ensure that your request body is valid and formatted correctly.| |optional |
&nbsp;&nbsp;| enable| Indicates if this setting is enabled.| optional |
&nbsp;|spam_check |This allows you to test the content of your email for spam. | |optional |
&nbsp;&nbsp;|enable | Indicates if this setting is enabled.| optional |
&nbsp;&nbsp;|post_to_url | An Inbound Parse URL that you would like a copy of your email along with the spam report to be sent to.| optional |
&nbsp;&nbsp;| threshold | The threshold used to determine if your content qualifies as spam on a scale from 1 to 10, with 10 being most strict, or most likely to be considered as spam.| optional |
|personalizations | An array of messages and their metadata. Each object within personalizations can be thought of as an envelope - it defines who should receive an individual message and how that message should be handled.| ||required |
&nbsp;|to| An array of recipients. Each object within this array may contain the name, but must always contain the email, of a recipient.|| required|
&nbsp;&nbsp;|email | Email | required |
&nbsp;&nbsp;|name | The name of the person or company that is sending the email.| optional|
&nbsp;|bcc | An array of recipients who will receive a blind carbon copy of your email. Each object within this array may contain the name, but must always contain the email, of a recipient.| |optional |
&nbsp;&nbsp;|email | Email | required |
&nbsp;&nbsp;|name | The name of the person or company that is sending the email. | optional|
&nbsp;|cc | An array of recipients who will receive a copy of your email. Each object within this array may contain the name, but must always contain the email, of a recipient.|| optional |
&nbsp;&nbsp;|email | Email | required |
&nbsp;&nbsp;|name | The name of the person or company that is sending the email. | optional|
&nbsp;|custom_args| Values that are specific to this personalization that will be carried along with the email and its activity data. Substitutions will not be made on custom arguments, so any string that is entered into this parameter will be assumed to be the custom argument that you would like to be used. May not exceed 10,000 bytes.| | optional |
&nbsp;|headers| A collection of JSON key/value pairs allowing you to specify specific handling instructions for your email. You may not overwrite the following headers: x-sg-id, x-sg-eid, received, dkim-signature, Content-Type, Content-Transfer-Encoding, To, From, Subject, Reply-To, CC, BCC || optional|
&nbsp;|subject |The subject of your email. Char length requirements, according to the RFC - http://stackoverflow.com/questions/1592291/what-is-the-email-subject-length-limit#answer-1592310 | | required |
|reply_to | | required |
&nbsp;|email | Email | | required |
&nbsp;|name | The name of the person or company that is sending the email. || optional|
|sections| An object of key/value pairs that define block sections of code to be used as substitutions. The key/value pairs must be strings. ||| optional|
|send_at | A unix timestamp allowing you to specify when you want your email to be delivered. This may be overridden by the personalizations[x].send_at parameter. You can't schedule more than 72 hours in advance. If you have the flexibility, it's better to schedule mail for off-peak times. Most emails are scheduled and sent at the top of the hour or half hour. Scheduling email to avoid those times (for example, scheduling at 10:53) can result in lower deferral rates because it won't be going through our servers at the same times as everyone else's mail.||| optional |
|subject| The subject of your email. Char length requirements, according to the RFC - http://stackoverflow.com/questions/1592291/what-is-the-email-subject-length-limit#answer-1592310| ||required|
|template_id | The id of a template that you would like to use. If you use a template that contains a subject and content (either text or html), you do not need to specify those at the personalizations nor message level.| ||optional |
|dynamic_template_data| If `template_id` is specified, the key/value pair will be mapped in the template. See [Dynamic Template Data](https://sendgrid.com/docs/ui/sending-email/how-to-send-an-email-with-dynamic-transactional-templates/) for more details.| || optional |
|tracking_settings | Settings to determine how you would like to track the metrics of how your recipients interact with your email.| || optional |
&nbsp;|click_tracking| Allows you to track whether a recipient clicked a link in your email.|| optional|
&nbsp;&nbsp;|enable| Indicates if this setting is enabled.| optional|
&nbsp;&nbsp;|enable_text|Indicates if this setting should be included in the text/plain portion of your email. | optional|
&nbsp;|ganalytics |Allows you to enable tracking provided by Google Analytics. | | optional|
&nbsp;&nbsp;|enable | Indicates if this setting is enabled.| optional|
&nbsp;&nbsp;|utm_source Name of the referrer source. (e.g. Google SomeDomain.com or Marketing Email) | optional|
&nbsp;&nbsp;|utm_medium NAME OF YOUR MARKETING MEDIUM e.g. email| optional|
&nbsp;&nbsp;|utm_term IDENTIFY PAID KEYWORDS HERE| optional|
&nbsp;&nbsp;|utm_content USE THIS SPACE TO DIFFERENTIATE YOUR EMAIL FROM ADS| optional|
&nbsp;&nbsp;|utm_campaign The name of the campaign| optional|
&nbsp;|open_tracking |Allows you to track whether the email was opened or not, but including a single pixel image in the body of the content. When the pixel is loaded, we can log that the email was opened. | | optional |
&nbsp;&nbsp;|enable | Indicates if this setting is enabled.| optional|
&nbsp;&nbsp;|substitution_tag| Allows you to specify a substitution tag that you can insert in the body of your email at a location that you desire. This tag will be replaced by the open tracking pixel. | optional|
&nbsp;|subscription_tracking |Allows you to insert a subscription management link at the bottom of the text and html bodies of your email. If you would like to specify the location of the link within your email, you may use the substitution_tag. | | optional|
&nbsp;&nbsp;|enable | Indicates if this setting is enabled.| optional|
&nbsp;&nbsp;|html | HTML to be appended to the email, with the subscription tracking link. You may control where the link is by using the tag <% %>| optional| If you would like to unsubscribe and stop receiving these emails <% clickhere %>.
&nbsp;&nbsp;|substitution_tag| A tag that will be replaced with the unsubscribe URL. for example: [unsubscribe_url]. If this parameter is used, it will override both the text and html parameters. The URL of the link will be placed at the substitution tag’s location, with no additional formatting. | optional|
&nbsp;&nbsp;|text | Text to be appended to the email, with the subscription tracking link. You may control where the link is by using the tag <% %>| optional|

