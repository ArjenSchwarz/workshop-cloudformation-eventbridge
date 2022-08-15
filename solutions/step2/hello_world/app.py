import os
import subprocess


s3bucket = os.environ['S3bucket']


def lambda_handler(event, context):
    stackarn = event['resources'][0]
    args = ("./fog", "report", "--stackname", stackarn, "--latest", "--s3bucket", s3bucket, "--output", "html")
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    print(output)
