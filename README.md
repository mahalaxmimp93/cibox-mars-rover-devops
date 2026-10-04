# CIBOX Mars Rover – Python + Jenkins CI

## Requirements covered
Checkout/setup, linting, unit tests, SonarQube analysis with an enforced quality gate,
Docker build, automated container smoke test, and Artifactory Docker publication.

## Prerequisites
Python 3.12+, Docker, Git, Jenkins, SonarQube, and an Artifactory Docker registry.

## Local execution
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python rover.py input.txt
```

Expected:
```text
1 3 N
5 1 E
```

## Tests
```bash
pytest -q
ruff check .
```

## Docker
```bash
docker build -t cibox/rover:local .
docker run --rm cibox/rover:local
```

## Jenkins configuration
Configure a SonarQube installation named `sonarqube`, a SonarScanner tool named
`SonarScanner`, and an Artifactory credential named
`artifactory-docker-registry`. Configure the SonarQube webhook to Jenkins so
`waitForQualityGate` can receive the analysis result.

The Jenkins agent needs Python 3.12, Docker CLI/daemon access, Git and network access
to SonarQube and Artifactory.

## Input assumptions
Plateau lower-left is 0,0. Coordinates are non-negative integers. Rover positions must
remain within the plateau. Directions are N/E/S/W. Commands are L/R/M. Rovers execute
sequentially.

## Invalid cases
Malformed coordinates, invalid directions/commands, incomplete rover input, starting
outside the plateau, or a move beyond the plateau are rejected.

## Security
Secrets are kept in Jenkins credentials, not Git. Docker authentication uses
`--password-stdin`. The container runs as a non-root user. Dependencies are pinned.

## Known limitations
The exercise is a CLI application. The smoke test verifies expected output; a production
pipeline could additionally use an image vulnerability scanner such as Trivy. The
Jenkinsfile assumes a Docker-capable build agent.

## Suggested commits
- feat: implement mars rover navigation
- test: add rover unit and edge case tests
- build: containerize rover application
- ci: add Jenkins quality gates and artifact publication
- docs: add setup and troubleshooting guide
