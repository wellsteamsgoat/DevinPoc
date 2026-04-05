pipeline {
    agent any

    environment {
        PYTHON_VERSION = "3.9"
        VIRTUAL_ENV = "venv"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv ${VIRTUAL_ENV}
                    source ${VIRTUAL_ENV}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    source ${VIRTUAL_ENV}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Build & Package') {
            steps {
                // Setup virtualenv, install requirements, and build sdist/wheel
                sh """
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                python setup.py sdist bdist_wheel
                """
            }
        }

        stage('Test') {
            steps {
                sh '''
                    source ${VIRTUAL_ENV}/bin/activate
                    python -m pytest tests/ --junitxml=test-results.xml
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                // Archive created artifacts, typically in 'dist/'
                archiveArtifacts artifacts: 'dist/*.whl, dist/*.tar.gz', onlyIfSuccessful: true
            }
        }
    }
}
