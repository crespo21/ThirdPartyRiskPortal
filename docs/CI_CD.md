# CI/CD Pipeline for ThirdPartyRiskPortal

## Overview
Enterprise-grade CI/CD pipeline for continuous delivery to African financial institutions with focus on security, compliance, and reliability.

## Pipeline Architecture

### Multi-Environment Strategy
```
Development → Staging → UAT → Production
     ↓           ↓       ↓        ↓
   Feature    Integration System  Customer
   Testing      Testing   Testing Deployment
```

### Branch Strategy
- **main**: Production-ready code (protected)
- **develop**: Integration branch for features
- **feature/***: Individual feature development
- **hotfix/***: Critical production fixes
- **release/***: Release preparation branches

## GitHub Actions Workflows

### Complete CI/CD Pipeline
```yaml
name: ThirdPartyRiskPortal CI/CD
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  AZURE_RESOURCE_GROUP: tprm-prod-rg
  AZURE_LOCATION: southafricanorth

jobs:
  security-scan:
    name: Security & Compliance Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: python, javascript
      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'ThirdPartyRiskPortal'
          path: '.'
          format: 'ALL'
      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: reports/dependency-check-report.sarif

  backend-tests:
    name: Backend Tests & Quality
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: tprm_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run linting
        run: |
          cd backend
          flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
          black --check app/
          isort --check-only app/
      
      - name: Run type checking
        run: |
          cd backend
          mypy app/
      
      - name: Run pytest with coverage
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/tprm_test
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=html
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    name: Frontend Tests & Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js 18
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run ESLint
        run: |
          cd frontend
          npm run lint
      
      - name: Run TypeScript check
        run: |
          cd frontend
          npm run type-check
      
      - name: Run Jest tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: frontend/coverage/lcov.info
          flags: frontend
          name: frontend-coverage

  build-and-push:
    name: Build & Push Container Images
    runs-on: ubuntu-latest
    needs: [security-scan, backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      - name: Login to Azure Container Registry
        uses: azure/docker-login@v1
        with:
          login-server: tprmregistry.azurecr.io
          username: ${{ secrets.AZURE_ACR_USERNAME }}
          password: ${{ secrets.AZURE_ACR_PASSWORD }}
      
      - name: Build and push backend image
        run: |
          cd backend
          docker build -t tprmregistry.azurecr.io/tprm-backend:${{ github.sha }} .
          docker push tprmregistry.azurecr.io/tprm-backend:${{ github.sha }}
      
      - name: Build and push frontend image
        run: |
          cd frontend
          docker build -t tprmregistry.azurecr.io/tprm-frontend:${{ github.sha }} .
          docker push tprmregistry.azurecr.io/tprm-frontend:${{ github.sha }}

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Azure Container Instances
        run: |
          az container create \
            --resource-group tprm-staging-rg \
            --name tprm-backend-staging \
            --image tprmregistry.azurecr.io/tprm-backend:${{ github.sha }} \
            --registry-login-server tprmregistry.azurecr.io \
            --registry-username ${{ secrets.AZURE_ACR_USERNAME }} \
            --registry-password ${{ secrets.AZURE_ACR_PASSWORD }} \
            --ports 8000 \
            --environment-variables \
              DATABASE_URL="${{ secrets.STAGING_DATABASE_URL }}" \
              SECRET_KEY="${{ secrets.STAGING_SECRET_KEY }}"

  integration-tests:
    name: Integration Tests (Staging)
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      - name: Run Postman Collection
        run: |
          npx newman run scripts/tprm-integration-tests.postman_collection.json \
            --environment scripts/staging-environment.json \
            --reporters cli,junit \
            --reporter-junit-export test-results.xml
      
      - name: Publish test results
        uses: dorny/test-reporter@v1
        with:
          name: Integration Tests
          path: test-results.xml
          reporter: java-junit

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build-and-push, integration-tests]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy using Bicep
        run: |
          az deployment group create \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --template-file infrastructure/main.bicep \
            --parameters \
              environment=production \
              backendImage=tprmregistry.azurecr.io/tprm-backend:${{ github.sha }} \
              frontendImage=tprmregistry.azurecr.io/tprm-frontend:${{ github.sha }}
      
      - name: Run smoke tests
        run: |
          # Wait for deployment to complete
          sleep 60
          curl -f https://tprm-api.standardbank.co.za/health || exit 1
          curl -f https://tprm.standardbank.co.za || exit 1
```

## Deployment Strategies

### Blue-Green Deployment
```bash
#!/bin/bash
# Blue-Green deployment script for zero-downtime updates

# Deploy to green environment
az container create \
  --resource-group tprm-prod-rg \
  --name tprm-backend-green \
  --image tprmregistry.azurecr.io/tprm-backend:${IMAGE_TAG}

# Health check green environment
health_check() {
  curl -f https://tprm-green.standardbank.co.za/health
}

# Wait for green to be healthy
until health_check; do
  echo "Waiting for green environment..."
  sleep 10
done

# Switch traffic to green
az network application-gateway rule update \
  --gateway-name tprm-appgw \
  --resource-group tprm-prod-rg \
  --name tprm-routing-rule \
  --backend-pool tprm-backend-green

# Cleanup blue environment after successful switch
az container delete \
  --resource-group tprm-prod-rg \
  --name tprm-backend-blue \
  --yes
```

### Canary Deployment
```yaml
# Canary deployment for gradual rollout
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: tprm-backend
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10   # 10% traffic to new version
      - pause: {duration: 10m}
      - setWeight: 25   # 25% traffic
      - pause: {duration: 10m}
      - setWeight: 50   # 50% traffic
      - pause: {duration: 10m}
      - setWeight: 100  # Full rollout
```

## Security & Compliance

### Secret Management
```yaml
# GitHub Secrets for CI/CD
AZURE_CREDENTIALS: Service Principal JSON
AZURE_ACR_USERNAME: Container Registry username
AZURE_ACR_PASSWORD: Container Registry password
DATABASE_URL: Production database connection
SECRET_KEY: Application secret key
AZURE_STORAGE_CONNECTION_STRING: Storage account
```

### Compliance Gates
- **SAST**: Static Application Security Testing (CodeQL)
- **DAST**: Dynamic Application Security Testing (OWASP ZAP)
- **SCA**: Software Composition Analysis (Dependency Check)
- **IaC Security**: Bicep template scanning (Checkov)

### Banking-Specific Validations
```python
# Custom pipeline steps for banking compliance
def validate_banking_compliance():
    """Validate banking-specific requirements"""
    checks = [
        validate_pii_encryption(),
        validate_audit_logging(),
        validate_access_controls(),
        validate_data_retention(),
        validate_backup_procedures()
    ]
    return all(checks)
```

## Monitoring & Alerting

### Pipeline Monitoring
- **Build Success Rate**: >95% target
- **Deployment Time**: <15 minutes end-to-end
- **Test Coverage**: >85% code coverage
- **Security Vulnerabilities**: Zero critical issues

### Production Monitoring
- **Application Performance**: Azure Application Insights
- **Infrastructure**: Azure Monitor
- **Logs**: Centralized logging with Azure Log Analytics
- **Alerts**: PagerDuty integration for critical issues

## Rollback Procedures

### Automated Rollback Triggers
```yaml
# Rollback triggers
rollback_conditions:
  - error_rate > 5%
  - response_time > 2000ms
  - health_check_failures > 3
  - security_incident_detected: true
```

### Manual Rollback Process
```bash
#!/bin/bash
# Emergency rollback script
PREVIOUS_VERSION=$(az container show \
  --resource-group tprm-prod-rg \
  --name tprm-backend \
  --query 'containers[0].image' -o tsv | cut -d: -f2)

# Deploy previous version
az container update \
  --resource-group tprm-prod-rg \
  --name tprm-backend \
  --image tprmregistry.azurecr.io/tprm-backend:${PREVIOUS_VERSION}
```

## Performance Optimization

### Build Optimization
- **Layer Caching**: Multi-stage Docker builds
- **Dependency Caching**: pip and npm cache strategies
- **Parallel Execution**: Matrix builds for multiple environments
- **Artifact Management**: Store and reuse build artifacts

### Deployment Optimization
- **Infrastructure as Code**: Bicep templates for consistency
- **Environment Parity**: Identical staging and production configs
- **Database Migrations**: Automated with rollback capability
- **Static Asset CDN**: Azure CDN for global performance
