pipeline {
    agent any

    environment {
        //PYTHON_VERSION = "3.9"
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
                sh 'python3 -m venv ${VIRTUAL_ENV}'
                sh 'echo ${WORKSPACE}'
                //sh 'source . ${WORKSPACE}/${VIRTUAL_ENV}/bin/activate'
                sh '${WORKSPACE}/${VIRTUAL_ENV}/bin/pip install --upgrade pip'
            }
        }

        stage('Install Dependencies') {
            steps {
                //sh 'source ${WORKSPACE}/${VIRTUAL_ENV}/bin/activate'
                sh '${WORKSPACE}/${VIRTUAL_ENV}/bin/pip install -r requirements.txt'
            }
        }

        stage('Build & Package') {
            steps {
                sh '${WORKSPACE}/${VIRTUAL_ENV}/bin/python setup.py sdist bdist_wheel'                
            }
        }

        stage('Test') {
            steps {
                sh '${WORKSPACE}/${VIRTUAL_ENV}/bin/python -m pytest tests/ --junitxml=test-results.xml'                
            }
        }

        stage('Archive Artifacts') {
            steps {
                script {
                    def server = Artifactory.server 'Artifactory'
                    def uploadSpec = """{
                        "files": [
                            {
                                "pattern": "dist/*.whl",
                                "target": "python/Devin/${BUILD_NUMBER}/"
                            }
                        ]
                    }"""
                    server.upload spec: uploadSpec
                }
            }
        }
    }
}
