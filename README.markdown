# Alexa Dude Skill

TODO

## Dependencies

Installation requires a UNIX environment with:

- BASH
- Python 27
- PIP

## Setup and installation

1. Create an [Amazon Web Services](http://aws.amazon.com/) account
2. Run aws-setup.sh to create a Role, Lambda Function, and SNS Topic. (*It will run `aws configure`, so have an key id and access key ready*)
3. Go to developer.amazon.com and create a Skill mapped to the Lambda function ARN, intentSchemas and sample utterances are in `config/`.
