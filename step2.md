# Step 2: Build a reporting tool

In this step we'll take our learnings from the first step and focus on building some reporting around our CloudFormation templates. For this we'll be using the tool [fog](https://github.com/ArjenSchwarz/fog#fog-report), which has the capability of generating reports about a deployment. You can see an example report when you follow that link, but in short it will show an overview of the changes that were deployed (at the resource level) and a diagram of when each of these steps took place.

What we will do here is trigger a function that creates a report like this every time a CloudFormation deployment finishes and store this in an S3 bucket. While the workshop will show the usefulness of fog, the goal isn't around the tool but around what you can do with this.

We'll be using [SAM](https://aws.amazon.com/serverless/sam/) for this step, but as always feel free to do things your own way.

## The solution

The complete solution, using Python and based on the helloworld SAM template can be found in [solutions/step2](./solutions/step2)

## 2.1 Create the SAM application

If you haven't installed SAM yet, please install it as per the instructions [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). Once you've got it running create your project with

```bash
sam init
```

In there, follow the steps to use one of the provided templates to create your application. Your best bet here might be the hello world template as that will allow you to pick any language you wish. Which language you use doesn't matter much, as we'll only be using the Lambda to run a binary. Because of that I suggest using either the latest supported version of Node (currently nodejs16.x for Lambda) or Python (python3.9). Then give it a fancy name like `step2` and we're good. When asked for X-Ray integration, we don't need that.

Once you have your sam project created, open the template.yaml file and remove anything in the `Events` part of the function as well as the `Outputs` section. If you chose the hello world template, it created an API Gateway and we don't use that, and the Outputs will contain references to it. We'll start filling things in again later.

## 2.2 Create an S3 bucket

In order to store the reports in an S3 bucket, we need that bucket to exist. For now create a standard private bucket (no public access) in your template. In order to ensure it's unique, I suggest a naming scheme that includes your account ID and region. The one used in the solution is:

```yaml
  ReportsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "cloudformation-reports-${AWS::AccountId}-${AWS::Region}"
```

By this stage, let's deploy our Lambda function to make sure it works correctly.

```bash
sam package --resolve-s3 --output-template-file packaged.yaml
sam deploy --template-file packaged.yaml --stack-name cfn-events-sam-step2 --capabilities CAPABILITY_IAM
```

The `--resolve-s3` flag above will create a bucket where SAM will upload the zip versions of your application. You can instead point it at your preferred bucket using the `--s3-bucket` flag.

If everything is correct, this will now deploy your S3 bucket and the so far unchanged Lambda function. Which isn't super useful, so let's make it do something.

## 2.3 Update the Lambda function

Our Lambda function only needs to do three things:

1. Parse the event it receives and pull out the arn of the CloudFormation stack.
2. Retrieve the S3 Bucket name
3. Run the binary.

Let's take these one at a time, but first let's clean up the contents of the Lambda function. Keep the handler function itself, but remove everything that's in there.

### 2.3.1 Parse the event

The event we will receive from EventBridge will be structured like this:

```json
{
  "version": "0",
  "id": "string",
  "detail-type": "CloudFormation Stack Status Change",
  "source": "string",
  "account": "string",
  "time": "string",
  "region": "string",
  "resources": ["string"],
  "detail": {
    "stack-id" : "string",
    "logical-resource-id" : "string",
    "physical-resource-id": "string",
    "status-details": {
        "status": "string",
        "status-reason": "string"
    },
     "resource-type": "string",
     "client-request-token": "string"
  }
}
```

There are two places where you can get the arn of the stack. It will be the only entry in the `resources` array, but it will also be stored in the `details.stack-id`. Pull this out and store it in a variable.

### 2.3.2 Get the S3 Bucket name

We'll pass the S3 Bucket as an environment variable, so you can just pull it in like that. Let's call it `S3Bucket` and store it as a variable as well.

### 2.3.3 Run the binary

First, we need the binary for fog. For this you'll need to download either the arm64 or amd64 Linux version from the [GitHub release page](https://github.com/ArjenSchwarz/fog/releases/tag/1.3.0) depending on the architecture you wish to use (unless you change it, that will be amd64). Make sure you use version 1.3 or newer to ensure it supports writing to S3. Unpack the zip file and copy or move the resulting binary to the directory containing your Lambda code.

We then need to update the code to run the function. For NodeJS you can do so using the [child_process](https://nodejs.org/api/child_process.html) function and for Python you can use [subprocess](https://docs.python.org/3/library/subprocess.html).

The command that needs to be run is the following:

```bash
./fog report --stackname ${stackarn} --latest --s3bucket ${s3bucket} --output html
```

Feel free to change the output format to `markdown` if you're happy to store them as markdown files instead.

And that's all we need to do for the function itself.

## 2.4 Update the template

And now we need to update the CloudFormation template. What we need to do here is:

1. Ensure the S3 bucket is passed as an environment variable
2. Ensure the function is allowed to write to the S3 bucket and has read access to CloudFormation stacks and CloudFormation stack events
3. Ensure the function is triggered when a CloudFormation stack is finished deploying

### 2.4.1 Add the S3 bucket as an evironment variable and fix the timeout

This is a matter of adding an `Environment` section to the function and in there a `Variables` section and then include a variable for the S3Bucket that points at your reports bucket. Ensure you use the same name as you called in the code in the previous step, which was `S3Bucket` if you used the suggested name.

A global timeout is defined at the top of the template, let's change that from 3 seconds to 10 seconds to ensure we don't run out of time. Alternatively, you can add a Timeout value to the function itself.

### 2.4.2 Grant correct permissions

SAM [provides some ready to use policy templates](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html), but unfortunately we can't use that for everything we need. We can use it for the S3 bucket though, so please add a `Policies` section to the function and include the `S3WritePolicy`. You'll need to define the `BucketName` argument for this as well.

For the CloudFormation access we need to grant an inline statement however as there is no template that grants everything we need. The statement we need is the below:

```yaml
        - Statement:
          - Sid: CloudFormationAccess
            Effect: Allow
            Action:
              - cloudformation:DescribeStacks
              - cloudformation:DescribeStackEvents
            Resource: !Sub "arn:${AWS::Partition}:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/*"
```

### 2.4.3 Ensure the function is triggered

Now we need to create a trigger for the function. There are two ways to do this. We could define the EventBridge rule similarly to how we did in step 1 and then link them together, but instead we can also define the Event inside the function. This works similar to how it was done for the API Gateway we removed at the start.

The Events structure we need is:

```yaml
      Events:
        Trigger:
          Type: CloudWatchEvent
          Properties:
            Pattern:
                # fill in the pattern here
```

You may notice I didn't provide the pattern. I'll leave that as an exercise for the reader as it will be similar to the one from [step 1](./step1.md). Just make sure to use the [correct status codes](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html#cli-stack-status-codes).

## 2.5 Deploy and test

And now it should all be working, so let's try it out by deploying it using the same commands as earlier:

```bash
sam package --resolve-s3 --output-template-file packaged.yaml
sam deploy --template-file packaged.yaml --stack-name cfn-events-sam-step2 --capabilities CAPABILITY_IAM
```

And if everything works as intended, this stack will be the first one to show up in your S3 bucket and you can download and view the report from there. If you want to confirm with a second stack, you can deploy [solutions/step2-teststack.yaml](solutions/step2-teststack.yaml).

## 2.6 Clean up the function (extremely optional)

To keep everything quick and straightforward (ish), we ended up with a function called HelloWorld. Feel free to fix the template up a bit so it looks cleaner. Similarly you can add some outputs or even write tests. None of this is done for the provided solution.

Go to [step 3](./step3.md)