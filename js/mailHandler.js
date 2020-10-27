
const lambdaConfig = {
    region: "ap-southeast-2",
    identityPoolId: "yourCognitoIdentifyPool",
    functionName: "YourLambdaFunctionName",
    clientContext: {
        "client": {
            "app_title": "YourAppName"
        }
    }
}

function sendMail(form, token = null){
    return new Promise((resolve, reject) => {
        var AWS = require('aws-sdk');

        AWS.config.update({
            region: lambdaConfig.region
        });

        AWS.config.credentials = new AWS.CognitoIdentityCredentials({
            IdentityPoolId: lambdaConfig.identityPoolId
        });

        var lambda = new AWS.Lambda({
            region: lambdaConfig.region,
        });

        var lambdaParams = {
            FunctionName: lambdaConfig.functionName,
            InvocationType: 'RequestResponse',
            LogType: 'None',
            ClientContext: AWS.util.base64.encode(JSON.stringify(lambdaConfig.clientContext)),
            Payload: JSON.stringify(parseForm(form, token)),
        }

        lambda.invoke(lambdaParams, function(error, data){
            if (error){
                console.log(error);
                var errorObj = {"error": "There was an error! (" + error.toString().substring(0, error.toString().indexOf(":")) + ")"};
                console.log(errorObj);
                reject(errorObj);
            }else{
                resolve(processResponse(JSON.parse(data.Payload)));
            }
        })
    });
}

function parseForm(form, token = null){
    var formData = {};
    form.forEach(object => {
        formData[object.name] = object.value;
    });
    formData["recaptchaToken"] = token;
    return formData
}

function processResponse(response){
    var output = {"fields": [], "formMessage": "", "response": response}

    if (response.statusCode != 200){
        if ("fields" in response){
            response["fields"].forEach(field => {
                let newField = {"name": field.name, "value": field.value}
                if ("errors" in field){
                    newField["errors"] = [];
                    field["errors"].forEach(error => {
                        newField["errors"].push(error);
                    });
                }
                output["fields"].push(newField);
            })
        }
        if ("error" in response){
        output["formMessage"] = {"error": response.error};
        }
        if ("message" in response && response.statusCode != 1001){
        output["formMessage"] = {"info": response.message};
        }
    }else{
        output["fieldErrors"] = {};
        output["formMessage"] = {"success": response.body};
    }
    console.log(output);
    return output;
}

module.exports.sendMail = sendMail;