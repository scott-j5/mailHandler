import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        SENDER = f'{event["name"]} <admin@byitegroup.com>'
        RECIPIENT = "admin@byitegroup.com"
        ##CONFIGURATION_SET = "ConfigSet"
        CHARSET = "UTF-8"
        AWS_REGION = "ap-southeast-2"
        SUBJECT = "Amazon SES Test (SDK for Python)"

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )

        # The HTML body of the email.
        BODY_HTML = """<html>
            <head></head>
            <body>
            <h1>Amazon SES Test (SDK for Python)</h1>
            <p>This email was sent with
                <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
                <a href='https://aws.amazon.com/sdk-for-python/'>
                AWS SDK for Python (Boto)</a>.</p>
            </body>
            </html>
            """    
    except Exception as e:
        print(e)
    else:
        # Create a new SES resource and specify a region.
        client = boto3.client('ses',region_name=AWS_REGION)

        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
                # If you are not using a configuration set, comment or delete the
                # following line
                #ConfigurationSetName=CONFIGURATION_SET,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])

event = {
    "name": "Scott James",
    "email": "scotty.james95@me.com",
    "message": "This is a test message",
    "phone_number": "0488465442",
}
lambda_handler(event, None)