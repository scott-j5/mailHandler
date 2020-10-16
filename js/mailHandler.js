
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

function sendMail(form){
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
            Payload: JSON.stringify(parseForm(form)),
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

function parseForm(form){
    var formData = {};
    form.forEach(object => {
        formData[object.name] = object.value;
    });
    return formData
}

module.exports.sendMail = sendMail;