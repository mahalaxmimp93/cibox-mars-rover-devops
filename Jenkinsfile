pipeline {
    agent any

    environment {
        // ============================================================
        // Docker configuration
        // ============================================================
        IMAGE_NAME = 'cibox/rover'
        IMAGE_TAG  = "${BUILD_NUMBER}"

        // ============================================================
        // SonarQube configuration
        // Jenkins:
        // Manage Jenkins -> Tools -> SonarQube Scanner installations
        // ============================================================
        SONAR_SCANNER = 'SonarScanner'

        // ============================================================
        // Artifactory configuration
        // This will be configured later.
        // ============================================================
        ARTIFACTORY_CREDENTIALS = 'artifactory-docker-registry'
        ARTIFACTORY_REGISTRY    = 'YOUR_ARTIFACTORY_REGISTRY'
    }

    stages {

        // ============================================================
        // 1. CHECKOUT
        // ============================================================
        stage('Checkout') {
            steps {
                echo '=============================================='
                echo 'Checking out source code from GitHub'
                echo '=============================================='

                checkout scm
            }
        }


        // ============================================================
        // 2. DOCKER CONNECTIVITY TEST
        // ============================================================
        stage('Docker Connectivity Test') {
            steps {
                echo '=============================================='
                echo 'Checking Docker connectivity from Jenkins'
                echo '=============================================='

                bat 'docker --version'
                bat 'docker version'
                bat 'docker info'
            }
        }


        // ============================================================
        // 3. PYTHON SETUP
        // ============================================================
        stage('Python Setup') {
            steps {
                echo '=============================================='
                echo 'Setting up Python virtual environment'
                echo '=============================================='

                bat 'python --version'

                bat 'python -m venv .venv'

                bat '.venv\\Scripts\\python.exe -m pip install --upgrade pip'

                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }


        // ============================================================
        // 4. LINT
        // ============================================================
        stage('Lint') {
            steps {
                echo '=============================================='
                echo 'Running Ruff lint checks'
                echo '=============================================='

                bat '.venv\\Scripts\\ruff.exe check .'
            }
        }


        // ============================================================
        // 5. UNIT TESTS
        // ============================================================
        stage('Unit Tests') {
            steps {
                echo '=============================================='
                echo 'Running Python unit tests'
                echo '=============================================='

                bat '''
                    .venv\\Scripts\\pytest.exe -q --junitxml=test-results.xml
                '''
            }

            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }


        // ============================================================
        // 6. SONARQUBE ANALYSIS
        // ============================================================
        stage('SonarQube Analysis') {
            steps {
                script {

                    echo '=============================================='
                    echo 'Running SonarQube analysis'
                    echo '=============================================='

                    def scannerHome = tool "${SONAR_SCANNER}"

                    withSonarQubeEnv('sonarqube') {

                        bat """
                            "${scannerHome}\\bin\\sonar-scanner.bat" ^
                            -Dsonar.projectKey=cibox-rover ^
                            -Dsonar.projectName="CIBOX Mars Rover" ^
                            -Dsonar.sources=. ^
                            -Dsonar.tests=tests ^
                            -Dsonar.python.version=3.12 ^
                            -Dsonar.exclusions=.venv/**,**/__pycache__/**,.pytest_cache/**,test-results.xml
                        """
                    }
                }
            }
        }


        // ============================================================
        // 7. SONARQUBE QUALITY GATE
        // ============================================================
        stage('Quality Gate') {
            steps {

                echo '=============================================='
                echo 'Waiting for SonarQube Quality Gate'
                echo '=============================================='

                timeout(time: 5, unit: 'MINUTES') {

                    waitForQualityGate abortPipeline: true
                }
            }
        }


        // ============================================================
        // 8. DOCKER BUILD
        // ============================================================
        stage('Docker Build') {
            steps {

                echo '=============================================='
                echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}"
                echo '=============================================='

                bat """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }


        // ============================================================
        // 9. DOCKER SMOKE TEST
        // ============================================================
        stage('Container Smoke Test') {
            steps {

                echo '=============================================='
                echo 'Running Docker container smoke test'
                echo '=============================================='

                /*
                 * Run the container and save its output.
                 *
                 * Expected application output:
                 *
                 * 1 3 N
                 * 5 1 E
                 */

                bat '''
                    docker run --rm %IMAGE_NAME%:%IMAGE_TAG% > container-output.txt
                '''

                echo 'Docker container output:'

                bat '''
                    type container-output.txt
                '''

                echo 'Validating expected Mars Rover output...'

                bat '''
                    findstr /x /c:"1 3 N" container-output.txt
                '''

                bat '''
                    findstr /x /c:"5 1 E" container-output.txt
                '''
            }
        }


        // ============================================================
        // 10. PUBLISH TO ARTIFACTORY
        // ============================================================
        stage('Publish to Artifactory') {

            /*
             * Artifactory is not configured yet.
             *
             * This stage will automatically be skipped until
             * ARTIFACTORY_REGISTRY is changed from:
             *
             * YOUR_ARTIFACTORY_REGISTRY
             *
             * to the actual Artifactory Docker registry.
             */

            when {
                expression {
                    return env.ARTIFACTORY_REGISTRY != 'YOUR_ARTIFACTORY_REGISTRY'
                }
            }

            steps {

                echo '=============================================='
                echo 'Publishing Docker image to Artifactory'
                echo '=============================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: "${ARTIFACTORY_CREDENTIALS}",
                        usernameVariable: 'ART_USER',
                        passwordVariable: 'ART_PASSWORD'
                    )
                ]) {

                    bat '''
                        echo %ART_PASSWORD% | docker login %ARTIFACTORY_REGISTRY% --username %ART_USER% --password-stdin

                        docker tag %IMAGE_NAME%:%IMAGE_TAG% %ARTIFACTORY_REGISTRY%/cibox/rover:%IMAGE_TAG%

                        docker push %ARTIFACTORY_REGISTRY%/cibox/rover:%IMAGE_TAG%

                        docker logout %ARTIFACTORY_REGISTRY%
                    '''
                }
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================
    post {

        always {

            echo '=============================================='
            echo 'Cleaning Jenkins workspace and Docker images'
            echo '=============================================='

            /*
             * Remove temporary Docker images.
             *
             * If cleanup fails, don't hide the actual pipeline result.
             */

            bat '''
                docker image prune -f || exit /B 0
            '''

            cleanWs()
        }


        success {

            echo '=============================================='
            echo '       CIBOX CI PIPELINE SUCCESSFUL'
            echo '=============================================='

            echo "Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
        }


        failure {

            echo '=============================================='
            echo '         CIBOX CI PIPELINE FAILED'
            echo '=============================================='

            echo 'Check the Jenkins Console Output for details.'
        }
    }
}
