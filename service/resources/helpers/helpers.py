import base64
import logging
from sendgrid.helpers.mail import (
    To, Cc, Bcc, Substitution, Header,
    CustomArg, Content, MimeType, Attachment, FileName,
    FileContent, FileType, Disposition, ContentId,
    Section, Category,
    IpPoolName, MailSettings, BccSettings, BccSettingsEmail,
    BypassListManagement, FooterSettings, FooterText,
    FooterHtml, SandBoxMode, SpamCheck, SpamThreshold, SpamUrl,
    TrackingSettings, ClickTracking, SubscriptionTracking,
    SubscriptionText, SubscriptionHtml, SubscriptionSubstitutionTag,
    OpenTracking, OpenTrackingSubstitutionTag, Ganalytics,
    UtmSource, UtmMedium, UtmTerm, UtmContent, UtmCampaign)

class HelperService():
    def getAttachments(self, attachments):
        """ This function sets up email attachments """
        try:
            # Python 3
            import urllib.request as urllib
        except ImportError:
            # Python 2
            import urllib2 as urllib
        attachment_list = []

        for attachment in attachments:
            if 'path' in attachment.keys() and attachment['path'] is not None and attachment['path'] != "":
                file_path = attachment['path']
                data = urllib.urlopen(file_path).read()
                encoded = base64.b64encode(data).decode()
            else:
                encoded = base64.b64encode(bytes(attachment['content'], 'utf-8')).decode()

            attachment_list.append(Attachment(
                FileContent(encoded),
                FileName(attachment['filename']),
                FileType(attachment['type'])
            ))

        return attachment_list

    def getEmailTrackings(self, settings):
        tracking_settings = TrackingSettings()
        if 'click_tracking' in settings.keys() and settings['click_tracking'] is not None:
            tracking_settings.click_tracking = ClickTracking(settings['click_tracking']['enable'], settings['click_tracking']['enable_text'])
        if 'open_tracking' in settings.keys() and settings['open_tracking'] is not None:
            tracking_settings.open_tracking = OpenTracking(
                settings['open_tracking']['enable'],
                OpenTrackingSubstitutionTag(settings['open_tracking']['substitution_tag'])
            )
        if 'subscription_tracking' in settings.keys() and settings['subscription_tracking'] is not None:
            tracking_settings.subscription_tracking = SubscriptionTracking(
                settings['subscription_tracking']['enable'],
                SubscriptionText(settings['subscription_tracking']['text']),
                SubscriptionHtml(settings['subscription_tracking']['html']),
                SubscriptionSubstitutionTag(settings['subscription_tracking']['substitution_tag']))
        if 'ganalytics' in settings.keys() and settings['ganalytics'] is not None:
            tracking_settings.ganalytics = Ganalytics(
                settings['ganalytics']['enable'],
                UtmSource(settings['ganalytics']['utm_source']),
                UtmMedium(settings['ganalytics']['utm_medium']),
                UtmTerm(settings['ganalytics']['utm_term']),
                UtmContent(settings['ganalytics']['utm_content']),
                UtmCampaign(settings['ganalytics']['utm_campaign'])
            )
        return tracking_settings

    def getCustomArgs(self, custom_args):
        custom_arg_list = []
        for custom_arg_key, custom_arg_value in custom_args.items():
            custom_arg_list.append(CustomArg(custom_arg_key, custom_arg_value))
        return custom_arg_list

    def getMailSettings(self, settings):
        mail_settings = MailSettings()
        if 'bcc' in settings.keys() and settings['bcc'] is not None:
            mail_settings.bcc_settings = BccSettings(
                settings['bcc']['enable'],
                BccSettingsEmail(settings['bcc']['email'])
            )
        if 'bypass_list_management' in settings.keys() and settings['bypass_list_management'] is not None:
            mail_settings.bypass_list_management = BypassListManagement(
                settings['bypass_list_management']['enable'])
        if 'footer' in settings.keys() and settings['footer'] is not None:
            mail_settings.footer_settings = FooterSettings(
                settings['footer']['enable'],
                FooterText(settings['footer']['text']),
                FooterHtml(settings['footer']['html'])
            )
        if 'sandbox_mode' in settings.keys() and settings['sandbox_mode'] is not None:
            mail_settings.sandbox_mode = SandBoxMode(settings['sandbox_mode']['enable'])
        if 'spam_check' in settings.keys() and settings['spam_check'] is not None:
            mail_settings.spam_check = SpamCheck(
                settings['spam_check']['enable'],
                SpamThreshold(settings['spam_check']['threshold']),
                SpamUrl(settings['spam_check']['post_to_url'])
            )
        return mail_settings

    def getSections(self, sections):
        email_sections = []
        for section_key, section_value in sections.items():
            email_sections.append(Section(section_key, section_value))
        return email_sections

    def getHeaders(self, headers):
        email_headers = []
        for header_key, header_value in headers.items():
            email_headers.append(Header(header_key, header_value))
        return email_headers

    def getCategory(self, categories):
        email_categories = []
        for category in categories:
            email_categories.append(Category(category))
        return email_categories

    def getEmails(self, emails, email_type):
        email_list = []
        counter = 0
        for email in emails:
            if email_type == 'to':
                email_list.append(To(email['email'], email['name'], p=counter))
            elif email_type == 'cc':
                email_list.append(Cc(email['email'], email['name'], p=counter))
            elif email_type == 'bcc':
                email_list.append(Bcc(email['email'], email['name'], p=counter))
            counter += 1
        return email_list

    def getContent(self, contents):
        content_list = []
        for content in contents:
            content_list.append(Content(content['type'], content['value']))
        return content_list
