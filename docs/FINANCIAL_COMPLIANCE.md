# Financial Compliance for Third-Party Risk Management

## Overview
This document maps regulatory compliance requirements (KYC, AML, POPIA/GDPR, SARB) to implemented features in the ThirdPartyRiskPortal platform tailored for African financial institutions, with specific focus on **South African Reserve Bank (SARB)** guidelines.

## KYC (Know Your Customer) Requirements
- **Data Captured**: Company name, registration number, incorporation date, principal officer, beneficial owners.
- **Schema Enforcement**: `CompanyCreate` Pydantic model validates KYC fields with regex (e.g. `^[0-9]{8,15}$` for IDs).
- **Endpoints**:
  - **POST** `/api/v1/companies/` to submit KYC data.
  - **GET** `/api/v1/companies/{company_id}` to retrieve KYC profile.
  - **PUT** `/api/v1/companies/{company_id}` to update and advance `kyc_status` (PENDING → VERIFIED/REJECTED).

## AML (Anti-Money Laundering) Requirements
- **Risk Scoring**: `Assessment` model includes `aml_score`, `aml_status` fields.
- **Screening Integration**: Dapr pub/sub component (`aml-screen`) triggers external watchlist API calls via `services/scoring.py`.
- **Workflow**:
  1. Create AML assessment via **POST** `/api/v1/assessments/` with `category='AML'`.
  2. Publish `aml-screen` event; scoring service calculates risk score.
  3. Update `aml_score` and set `aml_status` (PASS, REVIEW, FLAGGED).
- **Alerts**: High-risk assessments send notifications via Azure Service Bus binding.

## POPIA/GDPR Compliance Mapping
- **Data Encryption**: AES encryption at rest for PII in `security.py`.
- **Consent Management**: Audit log entry with `action='consent_given'` records user consents.
- **Data Subject Rights**:
  - **Erasure**: Soft delete and PII anonymization in **DELETE** `/api/v1/users/{user_id}`.
  - **Access**: Role-based filtering in **GET** `/api/v1/users/{user_id}` ensures only authorized roles view PII.

## SARB (South African Reserve Bank) Compliance
- **Operational Risk Framework**: `RiskFramework` model tracks operational risk categories per SARB guidelines.
- **Third-Party Risk Management**: Native implementation of SARB's third-party risk management requirements.
- **Data Governance**: Structured data classification following SARB's data governance principles.
- **Endpoints**:
  - **GET** `/api/v1/sarb/risk-profile/{company_id}` to retrieve SARB-compliant risk profile.
  - **POST** `/api/v1/sarb/regulatory-report` to generate SARB regulatory reports.
  - **PUT** `/api/v1/sarb/compliance-status/{assessment_id}` to update SARB compliance status.
- **Reporting**: Automated SARB regulatory reporting with required fields and formats.

## Audit Trail & Attestation Workflows
- **Audit Logs Table**: Tracks `user_id`, `entity`, `entity_id`, `action`, `timestamp`, `details`.
- **Endpoints**:
  - **GET** `/api/v1/audit-logs/` for querying logs with filters.
  - **POST** `/api/v1/audit-logs/` to manually record attestation events.
- **Attestation**: **PUT** `/api/v1/assessments/{id}/attest` adds approver signature and timestamp.

## Roles & Responsibilities
- **Roles**: `Role` enum includes ADMIN, ASSESSOR, APPROVER, USER.
- **RBAC**: Decorators in `auth.py` enforce roles (`require_roles(['APPROVER'])`).
- **Segregation of Duties**: Business logic prevents assessors from self-approving assessments.

## Configuration & Endpoint Reference
- **Environment Variables**:
  - `POPIA_ENABLED`, `AML_API_URL`, `AML_API_KEY`, `LOG_RETENTION_DAYS`.
- **Swagger Tags**: Grouped under `compliance` in OpenAPI docs.

## Testing & Validation
- **Unit Tests**: `tests/test_compliance.py` covers validators and status transitions.
- **Integration Tests**: Postman collection `scripts/compliance.postman_collection.json`.
- **Coverage**: Aim for ≥90% coverage on compliance modules.
