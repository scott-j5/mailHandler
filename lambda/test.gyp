import mailHandler

event = {
    "name": "Scott James",
    "email": "scotty.james95@me.com",
    "message": "This is a test message",
    "phone": "0488442",
    "recaptcha_token":"sdfidsn"
}
context = {
    "client": {
        "app_title": "kirkron"
    }
}
print(mailHandler.lambda_handler(event, context))