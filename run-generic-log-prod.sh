#!/usr/bin/env bash

export PYTHON_UNBUFFERED=1

.venv/bin/aws-log-watch-notifier \
	--aws-profile=arine-prod \
	--log-level=debug \
	notify \
	run \
	/aws/lambda/arine-prod_generic_log \
	https://hooks.slack.com/triggers/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 \
	--lambda-runtime-errors \
	--lambda-application-errors \
	--provisioned-throughput-exceeded
