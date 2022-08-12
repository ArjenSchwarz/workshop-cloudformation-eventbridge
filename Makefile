step1:
	fog deploy -n cfn-events-step1 -f step1-working -p step1-working -t default

step1-test:
	fog deploy -n cfn-events-step1-test -f step1-teststack -t default