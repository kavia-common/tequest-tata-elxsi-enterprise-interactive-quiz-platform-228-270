#!/bin/bash
cd /home/kavia/workspace/code-generation/tequest-tata-elxsi-enterprise-interactive-quiz-platform-228-270/TEQuestMonolithicContainer
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

