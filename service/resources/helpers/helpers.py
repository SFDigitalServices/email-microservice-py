import base64

class HelperService():
    # Email attachment
    def getAttachments(self, thisfile):
        """ This function sets up email attachments

        """
        from sendgrid.helpers.mail import (
            Mail, Attachment, FileContent, FileName,
            FileType, Disposition, ContentId)
        try:
            # Python 3
            import urllib.request as urllib
        except ImportError:
            # Python 2
            import urllib2 as urllib

        file_path = thisfile['path']
        data = urllib.urlopen(file_path).read()

        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType(thisfile['mimetype'])
        attachment.file_name = FileName(thisfile['name'])
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Unique file ID')

        return attachment