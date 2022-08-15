# Step 1: Alert on failures

In this first step we'll create an alert if a CloudFormation stack fails. In fact, we'll trigger it to send us the alert when it starts going into rollback mode. Why at this stage? Because it informs us quicker. Otherwise most likely our CI/CD system will already have the alert ready, but for some deployments a lengthy rollback can ensure that we aren't informed for half an hour or more that there was a failure. Which is not ideal. Getting these alerts earlier allows us to figure out what's wrong and create a solution.

## The solution

While you'll get more out of this if you do the work yourself, a working CloudFormation template containing the complete stack for step1 can be found at [solutions/step1.yaml](templates/step1-working.yaml). You will need to replace the `{{PUT YOUR EMAIL HERE}}` placeholder with your own email address. If you wish to use the Makefile to deploy it, you will need to make sure you have [fog](https://github.com/ArjenSchwarz/fog) present in your path. However, it's just a regular CloudFormation template so you can deploy it any way you see fit.

In addition, for this step only, solutions to each section are provided inside the section.


## 1.1 Create an SNS topic

First we want to create an SNS topic that will send us an email when we create the stack. You can easily create this topic and its subscription by hand, but let's use this to start our CloudFormation stack. You can copy the below and put it in a new CloudFormation file. Make sure you replace `{{PUT YOUR EMAIL HERE}}` with your own email address.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFormation and EventBridge workshop step 1
Resources:
  AlertSNSTopic:
    Type: AWS::SNS::Topic
    Properties:
      Subscription:
        - Endpoint: "{{PUT YOUR EMAIL HERE}}"
          Protocol: "email"
      TopicName: "CloudFormationAlertsStep1"
```

Now deploy it either from the CLI or through the CloudFormation Console. After it's been deployed you will receive an email at the address you added to verify that you want to receivee the notifications. Click the confirmation button in that email.

## 1.2 Ensure the SNS topic can be invoked by EventBridge

By default an SNS topic can't be triggered by a random service, so we need to add a policy to the topic that will allow it to be triggered by EventBridge. The below is a standard policy that allows any EventBridge rule to publish to the SNS Topic.

```yaml
  AlertSNSTopicPolicy:
    Type: 'AWS::SNS::TopicPolicy'
    Properties:
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: 'sns:Publish'
            Resource: '*'
      Topics:
        - !Ref AlertSNSTopic
```

## 1.3 Let's create the event rule

Now we need to create the event rule itself. If you use the Console, you'll need to do this in JSON (although part of it will be generated for you), but luckily CloudFormation supports YAML for it and the CDK has its own way of doing things as well. The things to pay attention to here are:

1. The source, this needs to be `"aws.cloudformation"` and provided as an array
2. The detail-type, this needs to be `"CloudFormation Stack Status Change"` exactly written like that and again provided as an array
3. The detail, here we want to only pay attention to the `status-details` and the `status` in there.

```yaml
  CloudFormationFailuresRule:
    Type: AWS::Events::Rule
    Properties:
      Name: CloudFormationFailedDeployments
      Description: "Notify on failed CloudFormation deployments"
      EventPattern:
        source:
          - "aws.cloudformation"
        detail-type:
          - "CloudFormation Stack Status Change"
        detail:
          status-details:
            status:
              - "ROLLBACK_IN_PROGRESS"
      State: "ENABLED"
      Targets:
        - Arn: !Ref AlertSNSTopic
          Id: "SNSAlerts"
```

Add the above to your template, deploy it, and verify in the Console that your rule has been created.

Because of the way statusses work in CloudFormation, the above only works for detecting rollbacks in newly created stacks. If you want it to respond to more statusses, you'll need to update the stack to support that. A complete list of valid statusses can be found [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html#cli-stack-status-codes). Make sure to add all relevant ROLLBACK_IN_PROGRESS items.

## 1.4 Time to test it works

A test stack is located in [solutions/step1-teststack.yaml](solutions/step1-teststack.yaml). This stack will attempt to create an S3 bucket with an existing name and therefore will fail. Deploy this using the command line or in the Console. If you wish to use the Makefile and have fog installed you can do so using `make step1-test`.

When you deploy this step you will notice it fails and you should receive an email about that.

## Homework

This falls outside of the workshop itself, but you will notice that while the message you receive contains all the information that it isn't the most readable. You can transform what EventBridge sends using an [Input Transformer](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-transform-target-input.html), or you can send it to a different service that can parse it for you.

[Click here to go to step 2](step2.md)