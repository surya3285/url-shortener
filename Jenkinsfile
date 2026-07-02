pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        // Public address used to build the short links returned by the API.
        // Replace with your EC2 public IP. Tip: attach an Elastic IP so this
        // doesn't change when the instance stops/starts.
        BASE_URL = 'http://13.63.46.21:8080'
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

        stage('Deploy') {
            // Only runs if the tests above passed (a failed stage aborts the run).
            steps {
                sh '''
                    set -e
                    # Rebuild images from the freshly checked-out code and
                    # recreate only the containers that changed. BASE_URL is
                    # picked up from the pipeline environment above.
                    docker compose up -d --build --remove-orphans
                    docker compose ps
                '''
            }
        }
    }

    post {
        success {
            echo "Deployed: tests green and containers restarted. App at ${env.BASE_URL}"
        }
        failure {
            echo 'Pipeline failed — check the stage logs above. Deploy was skipped.'
        }
    }
}
