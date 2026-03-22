pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh '. venv/bin/activate && python -m unittest discover -s tests'
            }
        }
    }
    post {
        always {
            junit 'tests/**/*.xml' // if you use a test runner that outputs JUnit XML
        }
    }
}
