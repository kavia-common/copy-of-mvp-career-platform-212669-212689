#!/bin/bash
cd /home/kavia/workspace/code-generation/copy-of-mvp-career-platform-212669-212689/CareerPlatformBackendAPI
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

