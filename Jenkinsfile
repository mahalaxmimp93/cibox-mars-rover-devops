pipeline {
    agent any

    environment {
        IMAGE_NAME = 'cibox/rover'
        IMAGE_TAG = "${BUILD_NUMBER}"
        ARTIFACTORY_REGISTRY = credentials('artifactory-docker-registry')
    }

    stages {
        stage('Checkout and Setup') {
            steps {
                checkout scm
                sh 'python3 --version'
                sh 'python3 -m venv .venv'
                sh '. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'
            }
        }

        stage('Validation / Lint') {
            steps {
                sh '. .venv/bin/activate && ruff check .'
            }
        }

        stage('Unit Tests') {
            steps {
                sh '. .venv/bin/activate && pytest -q --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scanner = tool 'SonarScanner'
                    withSonarQubeEnv('sonarqube') {
                        sh "${scanner}/bin/sonar-scanner " +
                           "-Dsonar.projectKey=cibox-rover " +
                           "-Dsonar.sources=. " +
                           "-Dsonar.tests=tests " +
                           "-Dsonar.python.version=3.12"
                    }
                }
            }
        }

        stage('Enforce Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Container Smoke Test') {
            steps {
                sh '''
                    set -e
                    output=$(docker run --rm ${IMAGE_NAME}:${IMAGE_TAG})
                    printf '%s\n' "$output"
                    echo "$output" | grep -qx "1 3 N"
                    echo "$output" | grep -qx "5 1 E"
                '''
            }
        }

        stage('Publish to Artifactory') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'artifactory-docker-registry',
                    usernameVariable: 'ART_USER',
                    passwordVariable: 'ART_PASSWORD'
                )]) {
                    sh '''
                        set -e
                        echo "$ART_PASSWORD" | docker login "$ARTIFACTORY_REGISTRY"                             --username "$ART_USER" --password-stdin
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG}                             "$ARTIFACTORY_REGISTRY/cibox/rover:${IMAGE_TAG}"
                        docker push "$ARTIFACTORY_REGISTRY/cibox/rover:${IMAGE_TAG}"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}
