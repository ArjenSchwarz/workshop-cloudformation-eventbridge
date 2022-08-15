step1:
	fog deploy -n cfn-events-step1 -f step1

step1-test:
	fog deploy -n cfn-events-step1-test -f step1-teststack

step2:
	curl -L -s https://github.com/ArjenSchwarz/fog/releases/download/1.3.0/fog-1.3.0-linux-amd64.tar.gz -o solutions/step2/hello_world/fog.tgz && cd solutions/step2/hello_world && tar xzf fog.tgz && rm fog.tgz
	cd solutions/step2 && sam package --resolve-s3 --output-template-file packaged.yaml
	cd solutions/step2 && sam deploy --template-file packaged.yaml --stack-name cfn-events-sam-step2 --capabilities CAPABILITY_IAM

step2-test:
	fog deploy -n cfn-events-step2-test -f step2-teststack

step3:
	cd solutions/step3 && sam package --resolve-s3 --output-template-file packaged.yaml
	cd solutions/step3 && sam deploy --template-file packaged.yaml --stack-name cfn-events-sam-step3 --capabilities CAPABILITY_IAM
