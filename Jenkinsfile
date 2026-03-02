pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('拉取代码') {
            steps { checkout scm }
        }
        stage('部署到服务器') {
            steps {
                sh 'bash scripts/deploy.sh'
            }
        }
    }

    post {
        success { echo '✅ 部署成功' }
        failure { echo '❌ 部署失败' }
    }
}
