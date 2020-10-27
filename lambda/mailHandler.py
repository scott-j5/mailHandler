import boto3
import json
import os
import re
import urllib3
from urllib.parse import urlencode

from botocore.exceptions import ClientError


class Email():
    # Set configuration values here
    _app_title = ''
    _aws_region = os.environ.get('REGION')
    _charset = "UTF-8"
    _sender = os.environ.get('SENDER')
    _recipient = os.environ.get('RECIPIENT')    
    _recaptcha_secret = os.environ.get("RECAPTCHA_SECRET")
    _recaptcha_score = 0.4
    _required_fields = ["recaptcha_token", "name", "email", "phone", "message"]

    # Initialise email class variables 
    def __init__(self, event, context):
        self.cleaned_fields = {}
        
        # If app_title is not provided in the client context as part of lambda invokation, 
        # set a default here
        if hasattr(context, 'client.app_title'):
            self.app_title = context.client.app_title
        else:
            self.app_title = 'Lambda'
        self.recaptcha_token = event.get("recaptcha_token", "")
        self.name = event.get("name", "")
        self.email = event.get("email", "")
        self.phone = event.get("phone", "")
        self.message = event.get("message", "")
        

    # Property to return a formatted text string from template, using email class variables
    @property
    def body_text(self):
        return open('template.txt').read().format(obj=self)

    # Property to return a formatted text string from template, using email class variables
    @property
    def body_html(self):
        return open('template.html').read().format(obj=self)

    # Return a formatted subject string from email class variables
    @property
    def subject(self):
        return f'{self.name} has made an enquiry on {self.app_title}'

    # Validate reCaptcha token using the recaptcha API 
    def validate_recaptcha(self, value):
        result = {"valid": False, "errors": []}
        params = {'secret': self._recaptcha_secret, 'response': self.recaptcha_token}
        api_url = f'https://www.google.com/recaptcha/api/siteverify?{urlencode(params)}'
        ## For local testing add cert_reqs='CERT_NONE' kwarg'
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')

        # Make request to reCaptcha API and read resonse to response_data variable
        response = http.request('POST', api_url)
        response_data = json.loads(response.data.decode("utf-8"))

        result['score'] = response_data.get('score', 0)
        if (response_data.get('success') and result['score'] >= self._recaptcha_score):
            result["valid"] = True
        else:
            result["errors"].append({"code": "422001", "message": 'Recaptcha validation failed. Are you sure you\'re not a robot? (Using incognito mode may cause this error)'})
        return result

    # Validate phone number inputs using regex query
    # Returns False if invalid
    def validate_phone(self, value):
        result = {"valid": False, "errors": []}
        if re.match(r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$', value):
            result["valid"] = True
        else:
            result["errors"].append({"code": "422002", "message":'Please enter a valid phone number!'})
        return result

    # Validate email inputs using regex query
    # Returns False if invalid
    def validate_email(self, value):
        result = {"valid": False, "errors": []}
        if re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', value):
            result["valid"] = True
        else:
            result["errors"].append({"code": "422003", "message":'Please enter a valid email address!'})
        return result
    
    # Reference function for choosing validation functions for certain field names
    # Similar functionality to a switch/case statement
    def validate(self, key):
        return{
            "email": self.validate_email,
            "phone": self.validate_phone,
            "recaptcha_token": self.validate_recaptcha,
        }.get(key, lambda *args: None)

    # Loop through each property of the email class, and validate.
    # Validation errors are appended to each field in cleaned_fields['errors']
    # Returns False if any validation errors
    def clean(self):
        clean = True

        # Convert properties of email class into a dict
        fields = {attr: value for attr, value in vars(self).items() if attr != 'cleaned_fields'}
        
        # Loop over dict of properties
        for key, value in fields.items():
            #Initialise a placeholder for errors
            errors = []

            #If field is in required_fields and is blank, append to errors
            #Else run custom validation function on field
            if key.lower() in self._required_fields and len(value) <= 0:
                errors.append({"code": "422000", "message": f'{key.capitalize()} is required!'})
                clean = False
            else:
                # Valid_check = the result of validation function on respective field
                valid_check = self.validate(key.lower())(value)
                # If fields validation function returns {"Valid": False} clean var is set to false to be returned
                if valid_check is not None and valid_check.get('valid') != True:
                    clean = False
                    errors.extend(valid_check['errors'])

            # Add cleaned field data to class variable cleaned_fields
            self.cleaned_fields[key] = {"name": key, "value": value, "errors": errors}
        return clean


def lambda_handler(event, context):
    # Create new email instance using data posted to lambda
    email = Email(event, context)

    # Clean email fields, returns False if any validation errors
    if email.clean():
        # Create a new SES resource and specify a region.
        client = boto3.client('ses', region_name=email._aws_region)

        # Try to send the email.
        try:
            # Provide the contents of the email.
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
                'body': json.dumps(f'Error! {e.response["Error"]["Message"]}'),
                'fields': email.cleaned_fields
            }
        # Display a success message if email was sent sucessfully
        else:
            return {
                'statusCode': 200,
                'body': json.dumps(f'Success! Enquiry sent. (ID: {response["MessageId"]})')
            }
    # Return cleaned email data (including erorrs) if any validation errors are raised
    else:
        return{
            'statusCode': 422,
            'message': 'UNPROCESSABLE ENTITY (Validation error)',
            'fields': email.cleaned_fields
        }