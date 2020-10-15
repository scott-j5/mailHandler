
const lambdaConfig = {
    region: "ap-southeast-2",
    identityPoolId: "ap-southeast-2:bf6adbef-7aba-4c4d-92c9-5a1b72adf53c",
    functionName: "kirkron-contact-email",
    clientContext: {
        "client": {
            "app_title": "kirkron"
        }
    }
}

export function invokeLambda(form){
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
            return errorObj;
        }else{
            console.log(data.Payload);
            return JSON.parse(data.Payload);
        }
    });
}

function parseForm(form){
    var formData = {};
    form.forEach(object => {
        formData[object.name] = object.value;
    });
    return formData
}