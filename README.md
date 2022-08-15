# CloudFormation and EventBridge workshop

Created by Arjen Schwarz for the AWS Programming and Tools Meetup.

## Background

Recently AWS introduced integration between EventBridge and CloudFormation. This enables a lot of possibilities around automation and in this workshop Arjen Schwarz, Principal Consultant at CMD, takes us through how to set this up, get automatic notifications when something goes wrong, and generate some reports about your deployment. And remember, if you're a fan of CDK that still uses CloudFormation under the hood so all of this is applicable to you.

During this workshop we'll be using CloudFormation, EventBridge, SNS, Lambda, S3, and any other tools that will be useful to you.

## How to follow this workshop

The workshop consists of several steps that all use the integration in different ways. The files named step1.md, step2.md, etc. can be followed in order. While for the sake of simplicity the steps all create a CloudFormation template, feel free to do it in CDK or any other way that feels comfortable for you. Of course, keep in mind that this is about the integration between CloudFormation and EventBridge so using something like Terraform may not be as useful.

At the end of each step there is the option to deploy a CloudFormation template to ensure that everything works. You can deploy these anyway you like, but the provided Makefile makes use of [fog](https://github.com/ArjenSchwarz/fog), a tool I wrote to make deploying CloudFormation easier.

## What will we be doing?

The below are demos that show some of the things that you can do and will teach you how to do them, but obviously your use cases for how you want to use this functionality might be different. In those cases, again feel free to use this to get up to speed on how it works or even use the provided code as a base for your own work.

### Step 1

Send a message through SNS when a stack deployment starts failing. Go to [step1](./step1.md).

### Step 2

Create a report about the deployment after it's finished deploying, and store this on S3. Go to [step2](./step2.md).

### Step 3

Run drift detection on a schedule, and trigger a notification when drift is detected. Go to [step3](./step3.md).