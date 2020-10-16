import boto3
import json
import re

from botocore.exceptions import ClientError


class Email():
    _sender = "Your Name <sendingemail@email.com>"
    _recipient = "recipientemail@email.com"
    _charset = "UTF-8"
    _aws_region = "ap-southeast-2"
    _app_title = ''
    _required_fields = ["name", "email", "phone", "message"]

    def __init__(self, event, context):
        if hasattr(context, 'client.app_title'):
            self.app_title = context.client.app_title
        else:
            self.app_title = 'Lambda'
        self.name = event["name"]
        self.email = event["email"]
        self.phone = event["phone"]
        self.message = event["message"]
        self.field_errors = {}

    def validate(self):
        self.clean()
        if len(self.field_errors) > 0:
            return False
        else:
            return True

    def clean(self):
        fields = {attr: value for attr, value in vars(self).items()}
        for key, value in fields.items():
            if key in self._required_fields and len(value) <= 0:
                self.field_errors[key] = f'{key.capitalize()} is required!'
            else:
                if key == 'email' and not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', value):
                    self.field_errors[key] = 'Please enter a valid email address!'
                if key == 'phone' and not re.match(r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$', value):
                    self.field_errors[key] = 'Please enter a valid phone number!'

    @property
    def body_text(self):
        return open('template.txt').read().format(obj=self)

    @property
    def body_html(self):
        return open('template.html').read().format(obj=self)

    @property
    def subject(self):
        return f'{self.name} has made an enquiry on {self.app_title}'

def lambda_handler(event, context):
    email = Email(event, context)

    if email.validate():
        # Create a new SES resource and specify a region.
        client = boto3.client('ses', region_name=email._aws_region)

        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        email._recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': email._charset,
                            'Data': email.body_html,
                        },
                        'Text': {
                            'Charset': email._charset,
                            'Data': email.body_text,
                        },
                    },
                    'Subject': {
                        'Charset': email._charset,
                        'Data': email.subject,
                    },
                },
                Source=email._sender,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e)
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error! {e.response["Error"]["Message"]}')
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps(f'Success! Enquiry sent. (ID: {response["MessageId"]})')
            }
    else:
        return{
            'statusCode': 1001,
            'message': 'Validation error',
            'field_errors': email.field_errors
        }