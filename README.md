# ThirdPartyRiskPortal - Enterprise Edition

A comprehensive Third Party Risk Management (TPRM) platform built with modern enterprise architecture, featuring React frontend, Python FastAPI backend, Azure Storage integration, and Dapr service orchestration.

## 🏗️ Architecture Overview

```
ThirdPartyRiskPortal/
├── frontend/                 # React TypeScript frontend
├── backend/                  # Python FastAPI backend
├── dapr/                     # Dapr configuration and components
├── infrastructure/           # Azure infrastructure as code
├── docs/                     # Documentation
└── scripts/                  # Deployment and utility scripts
```

## 🚀 Key Features

- **Modern React Frontend**: TypeScript, Material-UI, React Query, Context API
- **Secure Python Backend**: FastAPI, SQLAlchemy, Pydantic, OAuth2/JWT
- **Azure Storage Integration**: Secure file uploads with SAS tokens
- **Dapr Service Orchestration**: Service-to-service communication, state management
- **Enterprise Security**: RBAC, input validation, HTTPS, secrets management
- **Monitoring & Observability**: Azure Application Insights, structured logging
- **CI/CD Pipeline**: Automated testing, deployment, and monitoring

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.9+
- Azure CLI and subscription
- Docker and Docker Compose
- Dapr CLI

## 🛠️ Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Dapr Setup
```bash
dapr init
dapr run --app-id tprm-backend --app-port 8000 -- python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Azure Storage Setup
```bash
# Configure Azure Storage account and update environment variables
az storage account create --name tprmstorage --resource-group tprm-rg --location eastus --sku Standard_LRS
```

## 🔧 Configuration

### Environment Variables

Create `.env` files in both `frontend/` and `backend/` directories:

**Backend (.env)**
```env
DATABASE_URL=sqlite:///./tprm.db
SECRET_KEY=your-secret-key
AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection-string
AZURE_STORAGE_ACCOUNT_NAME=your-storage-account-name
AZURE_STORAGE_ACCOUNT_KEY=your-storage-account-key
AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_AZURE_STORAGE_ACCOUNT_NAME=your-storage-account-name
```

## 🏛️ Architecture Components

### Frontend (React + TypeScript)
- **State Management**: React Context API + React Query
- **UI Framework**: Material-UI (MUI)
- **HTTP Client**: Axios with interceptors
- **Form Handling**: React Hook Form + Yup validation
- **File Upload**: Azure Blob Storage integration

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: SQLAlchemy with async support
- **Authentication**: OAuth2 with JWT tokens
- **File Storage**: Azure Blob Storage with SAS tokens
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger

### Dapr Integration
- **Service Discovery**: Automatic service-to-service communication
- **State Management**: Redis for distributed state
- **Pub/Sub**: Event-driven architecture
- **Bindings**: Azure Storage, Azure Service Bus
- **Observability**: Distributed tracing and metrics

### Azure Storage Security
- **SAS Tokens**: On-demand generated for secure file access
- **Container Policies**: Role-based access control
- **Encryption**: At-rest and in-transit encryption
- **Audit Logging**: Comprehensive access logging

## 🔒 Security Features

- **Authentication**: OAuth2 with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Comprehensive validation at API boundaries
- **HTTPS**: TLS 1.3 encryption
- **Secrets Management**: Azure Key Vault integration
- **Audit Logging**: Complete audit trail for compliance

## 📊 Monitoring & Observability

- **Application Insights**: Performance monitoring and error tracking
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Endpoint health monitoring
- **Metrics**: Custom business metrics and KPIs
- **Distributed Tracing**: Request flow tracking across services

## 🧪 Testing Strategy

- **Unit Tests**: Jest (frontend) + pytest (backend)
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Playwright for full user journey testing
- **Security Tests**: OWASP ZAP integration
- **Performance Tests**: Load testing with k6

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Azure Container Instances or AKS
az container create --resource-group tprm-rg --name tprm-backend --image tprm-backend:latest
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [documentation](docs/)
- Review the [troubleshooting guide](docs/troubleshooting.md)
