# 🎬 Netflix Static — CI/CD Pipeline with Jenkins, AWS ECR & ECS Fargate

![Pipeline](https://img.shields.io/badge/CI%2FCD-Jenkins-blue?style=flat-square&logo=jenkins)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=flat-square&logo=docker)
![AWS ECR](https://img.shields.io/badge/Registry-AWS%20ECR-FF9900?style=flat-square&logo=amazon-aws)
![AWS ECS](https://img.shields.io/badge/Deploy-AWS%20ECS%20Fargate-FF9900?style=flat-square&logo=amazon-aws)
![Flask](https://img.shields.io/badge/App-Flask-000000?style=flat-square&logo=flask)
![ARM64](https://img.shields.io/badge/Architecture-ARM64-green?style=flat-square)

A Netflix-inspired static movie browsing app built with Flask, containerized with Docker, and deployed to AWS ECS Fargate via a fully automated Jenkins CI/CD pipeline.

---

## 📸 App Preview

The app features:
- 🎥 Hero banner section with featured movie
- 🎞️ Movie rows organized by genre
- 🖱️ Hover effects on movie cards
- 🪟 Movie detail modal popup
- 📄 Full movie detail page
- 🔴 Netflix-style dark UI

---

## 🏗️ Architecture

```
Developer pushes code
        │
        ▼
  GitHub Repository
        │
        ▼ (SCM polling / webhook)
    Jenkins CI
        │
        ├── 1. Checkout code
        ├── 2. Assume IAM Role (STS)
        ├── 3. Build Docker image (ARM64)
        ├── 4. Push to AWS ECR
        ├── 5. Deploy to ECS Fargate
        ├── 6. Wait for stabilization
        └── 7. Manual approval gate
                │
                ▼
        ECS Fargate (ARM64)
                │
                ▼
        Flask App live on public IP
```

---

## 📁 Project Structure

```
netflix-static/
├── app/
│   ├── __init__.py          # Flask app factory
│   └── routes.py            # Route definitions
├── static/
│   ├── css/
│   │   └── style.css        # Netflix-style CSS
│   └── js/
│       └── main.js          # Modal & navbar JS
├── templates/
│   ├── base.html            # Base layout with navbar & modal
│   ├── index.html           # Home page with hero & genre rows
│   └── movie.html           # Movie detail page
├── tests/
│   ├── __init__.py
│   └── test_app.py          # pytest test suite
├── app.py                   # Application entry point
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
└── Jenkinsfile              # CI/CD pipeline definition
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Application | Python 3.12, Flask 3.0.3, Gunicorn |
| Containerization | Docker (ARM64) |
| CI/CD | Jenkins |
| Container Registry | AWS ECR |
| Deployment | AWS ECS Fargate (ARM64) |
| Logging | AWS CloudWatch |
| IAM | AWS IAM Roles (STS AssumeRole) |
| Infrastructure | AWS VPC, Subnets, Security Groups |

---

## ⚙️ Prerequisites

### Local Machine
- Docker installed and running
- Git
- Python 3.12+

### Jenkins Server (Raspberry Pi / ARM64)
- Jenkins installed and running
- Docker installed (`jenkins` user in `docker` group)
- AWS CLI v2 installed
- Python 3.12 with `venv`

### AWS Account
- IAM user `jenkins-assumer` with `sts:AssumeRole` permission
- IAM role `JenkinsDeployRole` with ECR, ECS, EC2, and CloudWatch permissions
- IAM role `ecsTaskExecutionRole` with `AmazonECSTaskExecutionRolePolicy`

---

## 🔐 IAM Setup

### 1. Create the Deploy Role

```bash
# Trust policy — allows jenkins-assumer user to assume this role
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT_ID>:user/jenkins"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "netflix-flask-website"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
    --role-name JenkinsDeployRole \
    --assume-role-policy-document file://trust-policy.json
```

### 2. Attach Permissions to the Role

```bash
# ECR permissions
aws iam put-role-policy \
    --role-name JenkinsDeployRole \
    --policy-name JenkinsECRPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "ecr:GetAuthorizationToken",
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:CreateRepository",
                    "ecr:DescribeRepositories",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage",
                    "ecr:ListImages"
                ],
                "Resource": "arn:aws:ecr:us-east-1:<ACCOUNT_ID>:repository/*"
            }
        ]
    }'

# ECS, EC2, CloudWatch, and IAM PassRole permissions
aws iam put-role-policy \
    --role-name JenkinsDeployRole \
    --policy-name JenkinsECSPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecs:CreateCluster",
                    "ecs:DescribeClusters",
                    "ecs:RegisterTaskDefinition",
                    "ecs:DescribeTaskDefinition",
                    "ecs:ListTaskDefinitions",
                    "ecs:CreateService",
                    "ecs:UpdateService",
                    "ecs:DescribeServices",
                    "ecs:ListTasks",
                    "ecs:DescribeTasks"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeSubnets",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeSecurityGroups",
                    "ec2:CreateSecurityGroup",
                    "ec2:AuthorizeSecurityGroupIngress",
                    "ec2:DescribeNetworkInterfaces"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                    "logs:GetLogEvents"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole"
            }
        ]
    }'
```

### 3. Create ECS Task Execution Role

```bash
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### 4. Create the Assumer IAM User

```bash
aws iam create-user --user-name jenkins

aws iam put-user-policy \
    --user-name jenkins \
    --policy-name AssumeDeployRole \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/JenkinsDeployRole"
        }]
    }'

# Generate access keys — save these for Jenkins credentials
aws iam create-access-key --user-name jenkins
```

---

## 🔑 Jenkins Credentials Setup

Go to **Manage Jenkins → Credentials → System → Global → Add Credentials**

Add these four credentials:

| ID | Kind | Value |
|----|------|-------|
| `aws-access-key-id` | Secret text | AccessKeyId from `jenkins` IAM user |
| `aws-secret-access-key` | Secret text | SecretAccessKey from `jenkins` IAM user |
| `aws-role-arn` | Secret text | `arn:aws:iam::<ACCOUNT_ID>:role/JenkinsDeployRole` |
| `tmdb-api-key` | Secret text | *(optional — not used in static version)* |

---

## 🚀 Jenkins Pipeline Setup

1. Go to `http://localhost:8080` → **New Item**
2. Name: `netflix-static-pipeline` → **Pipeline** → **OK**
3. Under **Build Triggers** → check **Poll SCM** → schedule: `H/5 * * * *`
4. Under **Pipeline** → **Pipeline script from SCM**
5. SCM: **Git** → enter your repo URL
6. Script Path: `Jenkinsfile`
7. **Save** → **Build Now**

---

## 📋 Pipeline Stages

```
┌─────────────────────────────────────────────────────────┐
│                    Jenkins Pipeline                      │
├──────────────┬──────────────────────────────────────────┤
│ Stage        │ What it does                             │
├──────────────┼──────────────────────────────────────────┤
│ Checkout     │ Pulls latest code from Git               │
│ Assume Role  │ Gets temporary AWS credentials via STS   │
│ Build        │ Builds Docker image (ARM64, no cache)    │
│ Push to ECR  │ Creates ECR repo if needed, pushes image │
│ Deploy       │ Registers task def, creates/updates ECS  │
│              │ service, waits for stabilization,        │
│              │ prints public IP                         │
│ Approval     │ Manual gate — Approve or Rollback        │
├──────────────┴──────────────────────────────────────────┤
│ Post (always)│ Clears AWS credentials, prunes images,   │
│              │ cleans workspace                         │
└─────────────────────────────────────────────────────────┘
```

### Manual Approval Gate

After deployment, the pipeline pauses and presents:

```
🎬 Netflix app is live! Approve to finalize?

Action:  [ Approve ▼ ]   or   [ Rollback ▼ ]
Notes:   [ optional notes field ]

[ Approve & Clean Up ]
```

- **Approve** — keeps the deployment, runs cleanup
- **Rollback** — reverts to the previous ECS task definition revision
- **Timeout** — auto-approves after 30 minutes if no response

---

## 🐳 Docker

### Build Locally

```bash
docker build -t netflix-static:local .
```

### Run Locally

```bash
docker run -p 5000:5000 netflix-static:local
```

Open **http://localhost:5000**

### Important: ARM64 Architecture

This project runs on a **Raspberry Pi (ARM64)** Jenkins server. The Docker image is built natively for `ARM64` and deployed to **ECS Fargate ARM64**. This avoids QEMU cross-compilation issues.

The task definition specifies:
```json
"runtimePlatform": {
    "cpuArchitecture": "ARM64",
    "operatingSystemFamily": "LINUX"
}
```

> ⚠️ If you run this on an x86_64 Jenkins server, remove the `--runtime-platform` flag from the task definition registration and remove `DOCKER_DEFAULT_PLATFORM` from the build command.

---

## 🧪 Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

Tests cover:
- `GET /` returns 200
- `GET /health` returns `{"status": "ok"}`
- `GET /movie/<id>` returns 200 for valid movie
- `GET /movie/<id>` returns 404 for invalid movie

---

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | No | Set to `production` in ECS |

No external API keys required — all movie data is hardcoded.

---

## 📊 AWS Resources Created by Pipeline

The pipeline automatically creates these resources if they don't exist:

| Resource | Name |
|----------|------|
| ECR Repository | `netflix-static` |
| ECS Cluster | `netflix-static-cluster` |
| ECS Service | `netflix-static-service` |
| ECS Task Definition | `netflix-static-task` |
| CloudWatch Log Group | `/ecs/netflix-static-task` |
| Security Group | `netflix-static-sg` (port 5000 open) |

---

## 🌐 Accessing the App

After a successful deployment, the pipeline prints:

```
🎬 App is live at: http://<PUBLIC_IP>:5000
```

Navigate to that URL in your browser to see the app.

> 💡 **Note:** The public IP changes on every new task deployment. For a stable URL, set up an **Application Load Balancer (ALB)** in front of the ECS service.

---

## 🔍 Troubleshooting

### `exec format error` in ECS
Your image was built for the wrong architecture. Ensure your Jenkinsfile uses:
```groovy
sh "docker build -t ${IMAGE_URI} ."
```
And your task definition includes `--runtime-platform "cpuArchitecture=ARM64"`.

### `AccessDenied` on `sts:AssumeRole`
The `jenkins` IAM user is missing the `AssumeRole` permission or the role's trust policy doesn't include the user. Verify both with:
```bash
aws iam get-user-policy --user-name jenkins --policy-name AssumeDeployRole
aws iam get-role --role-name JenkinsDeployRole --query 'Role.AssumeRolePolicyDocument'
```

### ECS Service Not Stabilizing
Check service events:
```bash
aws ecs describe-services \
    --cluster netflix-static-cluster \
    --services netflix-static-service \
    --query 'services[0].events[:5]' \
    --output table
```

Check container logs:
```bash
LOG_STREAM=$(aws logs describe-log-streams \
    --log-group-name /ecs/netflix-static-task \
    --order-by LastEventTime \
    --descending \
    --query 'logStreams[0].logStreamName' \
    --output text)

aws logs get-log-events \
    --log-group-name /ecs/netflix-static-task \
    --log-stream-name "$LOG_STREAM" \
    --query 'events[*].message' \
    --output text
```

### `ecsTaskExecutionRole` Trust Error
```bash
aws iam update-assume-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'
```

### Docker Build Fails in Jenkins (Network Issue)
Add DNS to Docker daemon:
```bash
sudo tee /etc/docker/daemon.json << 'EOF'
{
    "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker
```

---

## 🔒 Security Best Practices Applied

- ✅ No long-lived AWS credentials in Jenkins — uses `sts:AssumeRole` with temporary credentials
- ✅ `ExternalId` on role trust policy prevents confused deputy attacks
- ✅ IAM user has only `sts:AssumeRole` permission — nothing else
- ✅ Temporary credentials cleared from AWS CLI config after every pipeline run
- ✅ Secrets stored in Jenkins Credentials Store — never in code
- ✅ Docker images scanned on push via ECR `scanOnPush=true`
- ✅ ECS task runs with least-privilege execution role

---

## 📈 Future Improvements

- [ ] Add Application Load Balancer for stable URL and HTTPS
- [ ] Add Route 53 custom domain
- [ ] Store movie data in DynamoDB instead of hardcoded list
- [ ] Add GitHub webhook for instant pipeline triggers instead of SCM polling
- [ ] Add Slack/email notifications on pipeline success/failure
- [ ] Add staging environment with promotion to production
- [ ] Implement ECS auto-scaling based on CPU/memory metrics

---

## 👤 Author

**Wadah Jameel**
- GitHub: [@wadah-jameel](https://github.com/wadah-jameel)

---

## 📄 License

This project is for educational purposes.
