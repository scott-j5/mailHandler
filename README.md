# Mail Handler
A simple DIY Mail API utilising an AWS hosted python Lambda script and JavaScript AWS_SDK on the front end, eliminating the need for an API gateway to invoke the lambda function.

# Setup
- Using IAM, set up a user with which to execute the lambda function. As this lambda will be using the SES service to send mail, appropriate permissions will be required to execute such tasks.
- Set up a cognito identity pool, this will be utilised by the front end to anonymously invoke the lambda function without the requirement for user credentials.
- Set up SES, ensuring any email addresses to be used for sending or recieving mail are verified within the SES console. (If you wish to send mail to unverified addresses you must contact AWS support to have your account removed from sandbox mode)
- Set up the lambda function, utilizing the users and user roles created in the steps above.
- Insert the code into the lambda function editor and test the code to ensure desired output
- The Lambda script will complete some basic validation on email and phone number fields, however custom validation functions can be added for additional fields if required.
- The lambda function will return either a success status with a success message or an error status with details of any errors including field validation errors in the following format:

  ## Success
        {
            statusCode: success_status_code,
            body: plain_text_success_message,
            message: plain_text_success_message
        }

  ## Error
        {
            statusCode: error_status_code,
            body: plain_text_description_of_error,
            message: plain_text_description_of_error,
            fields: {
                field1: {
                    name: field1,
                    value: recieved_value,
                    errors: [
                        {code: error_code, message: plain_text_description_of_error},
                        {code: error_code, message: plain_text_description_of_error}
                    ]
                }
                field2: {
                    name: field2,
                    value: recieved_value,
                    errors: [
                        {code: error_code, message: plain_text_description_of_error},
                        {code: error_code, message: plain_text_description_of_error}
                    ]
                }
            }
        }