# Step 3: Automated drift detection

In this optional step we'll look at another way CloudFormation can trigger EventBridge and build a simple notification for that. The trigger in this case is the detection of CloudFormation Drift results. CloudFormation drift is a functionality of CloudFormation that you can trigger and subsequently show whether there is any drift detected. Until the EventBridge integration the only way to discover this was by way of manually (or automatically) polling whether the results had arrived and if there was drift.

Building this is very similar to the first 2 steps, and builds on the knowledge you gained there. Because of this there won't be any hints as you should already know what to do.

## Solution

The solution is once again provided in [solutions/step3](solutions/step3).

## Step 3.1 Create a SAM application

We want to create a new SAM application, similar to step2. Again, pick your choice of language. The soultion uses Python, but please use the language you feel comfortable with. Clean up the function and template based on your experience for doing so in step 2.

## Step 3.2 Write the function

The function we want to create will be triggered on a schedule, and when running it will loop over all CloudFormation stacks and trigger the drift detection. What you need to do for this is retrieve a list of all CloudFormation stacks, loop over them, and run the drift detection command.

## Step 3.3 Ensure the function has all the required permissions

In order to run drift detection, the function needs read access to anything it needs to detect drift on. You can achieve this with the ReadOnlyAccess policy. In addition, it will need to have two CloudFormation specific permissions similar to how we granted permission in step2. The required permissions are:

```yaml
            Action:
              - cloudformation:DetectStackDrift
              - cloudformation:DetectStackResourceDrift
```



## Step 3.4 Add the SNS topic and EventBridge rule

The SNS topic setup is the same as in step1 and even the EventBridge is similar with the main difference being the `detail-type` value. Which should be `CloudFormation Drift Detection Status Change`. And make sure you fill in the `detail` part as well or you'll get multiple emails per stack.

The part you should care about is:

```yaml
        detail:
          status-details:
            stack-drift-status:
              - "DRIFTED"
```

At this stage you should be able to deploy and run a test for the function to see if it all works. You may need to edit the resources in an existing stack to trigger the drift.

## Step 3.5 Add the timer event trigger

Set up the Lambda function so it triggers on a daily basis.

## 3.6 Clean up the function (extremely optional)

To keep everything quick and straightforward (ish), we ended up with a function called HelloWorld. Feel free to fix the template up a bit so it looks cleaner. Similarly you can add some outputs or even write tests. None of this is done for the provided solution.