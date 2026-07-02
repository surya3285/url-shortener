pipeline {
    agent any

    options {
        timestamps()
        // Stop a run if it hangs (e.g. a Docker build wedging).
        timeout(time: 30, unit: 'MINUTES')
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
                        pip install -r requirements-dev.txt
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

        stage('Build images') {
            steps {
                // Confirms both Dockerfiles build (frontend build runs inside its image).
                sh 'docker compose build'
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded: tests green and images built.'
        }
        failure {
            echo 'Pipeline failed — check the stage logs above.'
        }
        cleanup {
            // Free workspace disk; keep the Jenkins node tidy.
            sh 'docker compose down --remove-orphans || true'
            cleanWs()
        }
    }
}
