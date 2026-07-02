pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    triggers {
        // Fires when GitHub sends a push webhook to /github-webhook/.
        // Requires the "GitHub" plugin and the job's
        // "GitHub hook trigger for GITScm polling" option enabled.
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend tests') {
            steps {
                dir('backend') {
                    sh '''
                        set -e
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements-test.txt
                        pytest -q --junitxml=../pytest-report.xml
                    '''
                }
            }
            post {
                always {
                    junit testResults: 'pytest-report.xml', allowEmptyResults: true
                }
            }
        }

        // NOTE: The Docker image build stage was removed to keep CI light
        // enough for a small (≈1 GB RAM) instance. Images are built on the
        // deploy host via `docker compose build`, not in CI. If you move to a
        // larger runner, re-add a stage that runs `docker compose build`.
    }

    post {
        success {
            echo 'Pipeline succeeded: backend tests green.'
        }
        failure {
            echo 'Pipeline failed — check the stage logs above.'
        }
        cleanup {
            // Keep the workspace tidy; no Docker teardown needed for tests-only CI.
            cleanWs()
        }
    }
}
