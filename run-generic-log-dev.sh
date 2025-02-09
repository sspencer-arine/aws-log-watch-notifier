#!/usr/bin/env bash

export PYTHON_UNBUFFERED=1

.venv/bin/aws-log-watch-notifier \
	--aws-profile=arine-dev \
	--log-level=debug \
	notify \
	run \
	/aws/lambda/integration_generic_log \
	https://hooks.slack.com/triggers/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 \
	--lambda-runtime-errors \
	--lambda-application-errors \
	--provisioned-throughput-exceeded
