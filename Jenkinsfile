pipeline {
  agent any

  parameters {
    string(name: 'APP_NAME', defaultValue: 'meuapp', description: 'Nome/slug do app (também usado como nome do container)')
    string(name: 'PORT', defaultValue: '8010', description: 'Porta pública no VPS (proxy NGINX -> container)')
    string(name: 'INTERNAL_PORT', defaultValue: '8000', description: 'Porta interna exposta pelo Uvicorn dentro do container')
    string(name: 'DOCKERFILE', defaultValue: 'Dockerfile', description: 'Caminho do Dockerfile')
    string(name: 'DOCKER_CONTEXT', defaultValue: '.', description: 'Contexto de build do Docker')
    booleanParam(name: 'TAG_LATEST', defaultValue: true, description: 'Também marcar a imagem como :latest')
  }

  environment {
    IMAGE = "local/${params.APP_NAME}:${env.BUILD_NUMBER}"
    REPO_IMAGE = "local/${params.APP_NAME}"
    CONTAINER = "${params.APP_NAME}"
  }

  triggers {
    githubPush()
  }

  options { timestamps() }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build image') {
      steps {
        sh '''
          set -eux
          OPTS=""
          if [ "${TAG_LATEST}" = "true" ]; then
            OPTS="-t ${REPO_IMAGE}:latest"
          fi
          docker build -f "${DOCKERFILE}" -t "${IMAGE}" $OPTS "${DOCKER_CONTEXT}"
        '''
      }
    }

    stage('Stop old container') {
      steps {
        sh 'docker rm -f "${CONTAINER}" || true'
      }
    }

    stage('Run new container') {
      steps {
        sh '''
          set -eux
          ENV_OPT=""
          if [ -f .env ]; then
            ENV_OPT="--env-file .env"
          fi
          docker run -d --name "${CONTAINER}" --restart unless-stopped \
            -p ${PORT}:${INTERNAL_PORT} \
            $ENV_OPT \
            "${IMAGE}"
        '''
      }
    }

    stage('Healthcheck') {
      steps {
        sh '''
          set -eux
          for endpoint in /health /; do
            if curl -fsS "http://localhost:${PORT}${endpoint}"; then
              exit 0
            fi
          done
          echo "Healthcheck failed"
          docker logs "${CONTAINER}" || true
          exit 1
        '''
      }
    }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
  }
}
