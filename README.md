Welcome to the 'Smart Garden' for  Alexa Skills Kit (Python)
=======================================================================================

This project enables Alexa to perform action in an indoor garden that is set with a Raspberry PI. This project provisions the Alexa skill that uses the custom interaction model, an AWS Lambda function, and an AWS CodePipeline continuous integration/continuous delivery (CI/CD) pipeline.

Pre-requisites
--------------
* You must already have created an [Amazon Developer account](https://developer.amazon.com/).

What's Here
-----------
* skill.json - contains the skill manifest that provides Alexa with your skill metadata. [See manifest documentation here](https://developer.amazon.com/docs/smapi/skill-manifest.html)
* interactionModels - contains interaction model files in JSON format. [See interaction model documentation here](https://developer.amazon.com/docs/smapi/interaction-model-schema.html).
  * en-GB.json - contains the interaction model for the en-GB locale.
* lambda - the parent folder that contains the code of all Lambda functions of this skill.
  * custom
    * lambda_function.py - contains the request handling code that will be deployed to AWS Lambda function.
    * requirements.txt - contains a list of dependencies to be installed.
* buildspec.yml - used by AWS CodeBuild to package the Lambda function code to be deployed by CodePipeline using CloudFormation.
* template.yml - the template with reference to Lambda function code to be deployed by CloudFormation.
* README.md - this file.

What Do I Do Next?
------------------
* The default invocation name of your skill is 'smart garden'.
* Test the 'smart garden' skill in the Alexa Simulator. From your AWS CodeStar project dashboard, choose the Alexa Simulator button. You can also go to the [Alexa Skills Kit developer console](https://developer.amazon.com/alexa/console/ask), select your skill, and choose the Test tab. Enable testing and type or say, "ask smart garden" or "tell smart garden".
* Once the skill is enabled in the Alexa Simulator, it can also be invoked on an Alexa enabled device which is registered with your Amazon developer account.