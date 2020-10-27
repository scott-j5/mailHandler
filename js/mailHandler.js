
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
                resolve(JSON.parse(data.Payload));
            }
        })
    });
}

function parseForm(form, token = null){
    var formData = {};
    form.forEach(object => {
        formData[object.name] = object.value;
    });
    formData["recaptcha_token"] = token;
    return formData
}

function formatResponse(response){
    var output = {"fields": [], "formMessages": [], "response": response}

    if (response.statusCode != 200){
        if ("fields" in response){
            output["fields"] = response["fields"];
            if (output['fields']['recaptcha_token']['errors'].length > 0){
                output['fields']['recaptcha_token']['errors'].forEach(error => {
                    output["formMessages"].push({"code": "", "type": "error", "message": error.message});
                });
            }
        }
        if ("error" in response){
            output["formMessages"].push({"code": "", "type": "error", "message": response.error});
        }
        if ("errorMessage" in response){
            output["formMessages"].push({"code": "", "type": "error", "message": response.errorMessage});
        }
        if ("message" in response && response.statusCode != 1001){
            output["formMessages"].push({"code": "", "type": "info", "message": response.message});
        }
    }else{
        output["fieldErrors"] = {};
        output["formMessages"] = {"code": "", "type": "success", "message": response.body};
    }
    return output;
}

module.exports.sendMail = sendMail;
module.exports.formatResponse = formatResponse;