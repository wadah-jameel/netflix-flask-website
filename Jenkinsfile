pipeline {
    agent any

    environment {
        AWS_REGION     = 'us-east-1'
        AWS_ACCOUNT_ID = '977305320020'
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPO       = 'netflix-static'
        IMAGE_TAG      = "${env.GIT_COMMIT?.take(7) ?: 'latest'}"
        IMAGE_URI      = "${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}"
        ECS_CLUSTER    = 'netflix-static-cluster'
        ECS_SERVICE    = 'netflix-static-service'
        TASK_FAMILY    = 'netflix-static-task'
        CONTAINER_PORT = '5000'
        EXTERNAL_ID    = 'netflix-flask-website'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log --oneline -3'
            }
        }

        stage('Assume IAM Role') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',     variable: 'ASSUMER_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'ASSUMER_SECRET'),
                    string(credentialsId: 'aws-role-arn',          variable: 'ROLE_ARN')
                ]) {
                    script {
                        sh """
                            aws configure set aws_access_key_id     ${ASSUMER_KEY_ID}
                            aws configure set aws_secret_access_key ${ASSUMER_SECRET}
                            aws configure set default.region        ${AWS_REGION}
                        """

                        def stsOutput = sh(
                            script: """
                                aws sts assume-role \
                                    --role-arn ${ROLE_ARN} \
                                    --role-session-name jenkins-${env.BUILD_NUMBER} \
                                    --external-id ${EXTERNAL_ID} \
                                    --duration-seconds 3600 \
                                    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
                                    --output text
                            """,
                            returnStdout: true
                        ).trim()

                        def parts = stsOutput.tokenize()
                        env.AWS_ACCESS_KEY_ID     = parts[0]
                        env.AWS_SECRET_ACCESS_KEY = parts[1]
                        env.AWS_SESSION_TOKEN     = parts[2]

                        sh 'aws sts get-caller-identity'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building ${IMAGE_URI}"
                sh "docker build -t ${IMAGE_URI} ."
            }
        }

        stage('Push to ECR') {
            steps {
                sh """
                    # Create ECR repo if it doesn't exist
                    aws ecr describe-repositories \
                        --repository-names ${ECR_REPO} \
                        --region ${AWS_REGION} 2>/dev/null || \
                    aws ecr create-repository \
                        --repository-name ${ECR_REPO} \
                        --region ${AWS_REGION} \
                        --image-scanning-configuration scanOnPush=true

                    # Authenticate Docker with ECR
                    aws ecr get-login-password --region ${AWS_REGION} \
                        | docker login --username AWS \
                          --password-stdin ${ECR_REGISTRY}

                    # Push commit-tagged image
                    docker push ${IMAGE_URI}

                    # Also tag and push as latest
                    docker tag  ${IMAGE_URI} ${ECR_REGISTRY}/${ECR_REPO}:latest
                    docker push ${ECR_REGISTRY}/${ECR_REPO}:latest

                    echo "✅ Image pushed: ${IMAGE_URI}"
                """
            }
        }

        stage('Deploy to ECS') {
            steps {
                script {
                    def taskFamily    = env.TASK_FAMILY
                    def ecrRepo       = env.ECR_REPO
                    def imageUri      = env.IMAGE_URI
                    def containerPort = env.CONTAINER_PORT
                    def ecsCluster    = env.ECS_CLUSTER
                    def ecsService    = env.ECS_SERVICE
                    def awsRegion     = env.AWS_REGION
                    def accountId     = env.AWS_ACCOUNT_ID

                    // Write container definitions to a file — avoids all JSON escaping issues
                    def containerDef = """[
                        {
                            "name": "${ecrRepo}",
                            "image": "${imageUri}",
                            "portMappings": [
                                {
                                    "containerPort": ${containerPort},
                                    "protocol": "tcp"
                                }
                            ],
                            "environment": [
                                {
                                    "name": "FLASK_ENV",
                                    "value": "production"
                                }
                            ],
                            "healthCheck": {
                                "command": [
                                    "CMD-SHELL",
                                    "curl -f http://localhost:5000/health || exit 1"
                                ],
                                "interval": 30,
                                "timeout": 5,
                                "retries": 3,
                                "startPeriod": 15
                            },
                            "logConfiguration": {
                                "logDriver": "awslogs",
                                "options": {
                                    "awslogs-group": "/ecs/${taskFamily}",
                                    "awslogs-region": "${awsRegion}",
                                    "awslogs-stream-prefix": "ecs"
                                }
                            }
                        }
                    ]"""

                    writeFile file: 'container-definitions.json', text: containerDef

                    // Validate JSON before sending to AWS
                    sh '''
                        python3 -c "
import json
with open('container-definitions.json') as f:
    json.load(f)
print('✅ Container definition JSON is valid')
"
                    '''

                    sh """
                        # Create CloudWatch log group if it doesn't exist
                        aws logs create-log-group \
                            --log-group-name /ecs/${taskFamily} \
                            --region ${awsRegion} 2>/dev/null || true

                        # Create ECS cluster if it doesn't exist
                        aws ecs describe-clusters \
                            --clusters ${ecsCluster} \
                            --region ${awsRegion} \
                            --query 'clusters[?status==`ACTIVE`].clusterName' \
                            --output text | grep -q ${ecsCluster} || \
                        aws ecs create-cluster \
                            --cluster-name ${ecsCluster} \
                            --region ${awsRegion}

                        echo "📋 Registering task definition..."
                        TASK_DEF_ARN=\$(aws ecs register-task-definition \
                            --family ${taskFamily} \
                            --network-mode awsvpc \
                            --requires-compatibilities FARGATE \
                            --cpu 256 \
                            --memory 512 \
                            --execution-role-arn arn:aws:iam::${accountId}:role/ecsTaskExecutionRole \
                            --container-definitions file://container-definitions.json \
                            --region ${awsRegion} \
                            --query 'taskDefinition.taskDefinitionArn' \
                            --output text)

                        echo "✅ Task definition: \$TASK_DEF_ARN"

                        # Check if service exists
                        SERVICE_EXISTS=\$(aws ecs describe-services \
                            --cluster ${ecsCluster} \
                            --services ${ecsService} \
                            --region ${awsRegion} \
                            --query 'services[?status==`ACTIVE`].serviceName' \
                            --output text)

                        if [ -z "\$SERVICE_EXISTS" ]; then
                            echo "🆕 Service not found — creating it..."

                            # Get default VPC subnet and security group
                            SUBNET_ID=\$(aws ec2 describe-subnets \
                                --filters Name=defaultForAz,Values=true \
                                --query 'Subnets[0].SubnetId' \
                                --output text \
                                --region ${awsRegion})

                            # Check if security group already exists
                            SG_ID=\$(aws ec2 describe-security-groups \
                                --filters Name=group-name,Values=netflix-static-sg \
                                --query 'SecurityGroups[0].GroupId' \
                                --output text \
                                --region ${awsRegion} 2>/dev/null)

                            if [ "\$SG_ID" = "None" ] || [ -z "\$SG_ID" ]; then
                                echo "🔒 Creating security group..."
                                SG_ID=\$(aws ec2 create-security-group \
                                    --group-name netflix-static-sg \
                                    --description "Netflix Static App" \
                                    --region ${awsRegion} \
                                    --query 'GroupId' \
                                    --output text)

                                aws ec2 authorize-security-group-ingress \
                                    --group-id \$SG_ID \
                                    --protocol tcp \
                                    --port ${containerPort} \
                                    --cidr 0.0.0.0/0 \
                                    --region ${awsRegion}
                            fi

                            echo "Subnet: \$SUBNET_ID | SG: \$SG_ID"

                            aws ecs create-service \
                                --cluster ${ecsCluster} \
                                --service-name ${ecsService} \
                                --task-definition \$TASK_DEF_ARN \
                                --desired-count 1 \
                                --launch-type FARGATE \
                                --network-configuration "awsvpcConfiguration={
                                    subnets=[\$SUBNET_ID],
                                    securityGroups=[\$SG_ID],
                                    assignPublicIp=ENABLED
                                }" \
                                --region ${awsRegion}

                            echo "✅ Service created!"
                        else
                            echo "🔄 Service exists — updating..."
                            aws ecs update-service \
                                --cluster ${ecsCluster} \
                                --service ${ecsService} \
                                --task-definition \$TASK_DEF_ARN \
                                --force-new-deployment \
                                --region ${awsRegion}
                        fi

                        echo "⏳ Waiting for service to stabilize..."
                        aws ecs wait services-stable \
                            --cluster ${ecsCluster} \
                            --services ${ecsService} \
                            --region ${awsRegion}

                        # Print the public IP of the running task
                        TASK_ARN=\$(aws ecs list-tasks \
                            --cluster ${ecsCluster} \
                            --service-name ${ecsService} \
                            --region ${awsRegion} \
                            --query 'taskArns[0]' \
                            --output text)

                        ENI_ID=\$(aws ecs describe-tasks \
                            --cluster ${ecsCluster} \
                            --tasks \$TASK_ARN \
                            --region ${awsRegion} \
                            --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
                            --output text)

                        PUBLIC_IP=\$(aws ec2 describe-network-interfaces \
                            --network-interface-ids \$ENI_ID \
                            --region ${awsRegion} \
                            --query 'NetworkInterfaces[0].Association.PublicIp' \
                            --output text)

                        echo "🎬 App is live at: http://\$PUBLIC_IP:${containerPort}"
                    """
                }
            }
        }
    }

stage('Approval') {
    steps {
        echo "🎬 App is deployed — review it before cleanup."
        timeout(time: 30, unit: 'MINUTES') {
            input(
                message: 'Pipeline complete. Approve to finish and clean up?',
                ok: 'Yes, clean up',
                submitter: 'admin',          // remove this line to allow anyone to approve
                parameters: [
                    choice(
                        name: 'ACTION',
                        choices: ['Approve', 'Rollback'],
                        description: 'Approve to keep deployment, Rollback to revert'
                    )
                ]
            )
        }
    }
}
