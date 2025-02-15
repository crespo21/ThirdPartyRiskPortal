# ThirdPartyRiskPortal

Below is a table summarizing the scope of work we've completed so far versus what remains to be implemented based on the TPRM data model documentation:

| **Component/Task**                                           | **Status**        | **Details**                                                                                                                                                         |
|--------------------------------------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Project Structure & Basic FastAPI Setup**                  | **Completed**     | Directory structure established; FastAPI application instance, basic routing, and dependency setup are in place.                                                     |
| **Database Integration (SQLite)**                            | **Completed**     | SQLite configured via SQLAlchemy; core models (e.g., `core_company`, risk assessments, tasks, etc.) are defined and table creation via SQLAlchemy is provided.   |
| **Basic CRUD API Endpoints**                                 | **Completed**     | Endpoints for creating and retrieving companies, assessments, tasks, and due diligence requests have been implemented.                                               |
| **OAuth2 Security & JWT Authentication**                     | **Completed**     | Basic authentication endpoints (e.g., token generation) using OAuth2 and JWT have been implemented.                                                                  |
| **Basic Testing Setup**                                      | **Completed**     | A testing framework with sample tests for main routes, models, and services is in place.                                                                              |
| **Azure Application Insights Monitoring (Basic)**            | **Completed**     | Basic monitoring integration is implemented (requires a valid instrumentation key to be fully active).                                                               |
| **Raw SQL Scripts for Core Tables**                          | **Provided**      | SQL queries for creating core tables (e.g., `core_company`, `sn_vdr_risk_asmt_assessment`, etc.) have been supplied.                                                  |
|                                                              |                   |                                                                                                                                                                     |
| **Event-Driven Management History & Rules**                  | **To Be Completed** | Implementation of `sn_tprm_dd_rule_execution_history` and `sn_tprm_dd_generation_rule` tables and their associated business logic.                                   |
| **Assessment Metric Types & Templates**                      | **To Be Completed** | Implementation of `asmt_metric_type` and `sn_vdr_risk_asmt_assessment_template` components, including their relationships with assessments.                        |
| **Engagement Risk Scoring Rule & Engagement Level Rating**     | **To Be Completed** | Implementation of `sn_vdr_risk_asmt_engagement_risk_scoring_rule` and `sn_vdr_risk_asmt_engagement_level_rating` for risk scoring on engagements.                   |
| **Risk & Control Components**                                | **To Be Completed** | Implementation of `sn_risk_risk` and `sn_compliance_control` tables along with their relationships and integration with the risk management process.                  |
| **Due Diligence Workflow (Complete Endpoints)**              | **To Be Completed** | Full implementation of the due diligence process endpoints, including tasks, statuses, and integration with other assessment components.                             |
| **Scoring Aggregation & Risk Calculation Logic**             | **To Be Completed** | Detailed logic to aggregate risk scores from internal, external, and tiering assessments; includes weighted calculations, min/max/avg aggregation, etc.                |
| **Many-to-Many Relationships**                               | **To Be Completed** | Implementation of join tables and endpoints for many-to-many relationships (e.g., between vendor contacts and companies, etc.).                                     |
| **Frontend Integration (e.g., React)**                       | **To Be Completed** | Complete front-end implementation to provide a user interface for managing assessments, due diligence, and risk monitoring, integrated with the FastAPI backend.     |
| **Role-Based Access Control (RBAC)**                         | **To Be Completed** | Detailed implementation of user roles and permissions across endpoints (e.g., admin, assessor, approver, etc.).                                                        |
| **Azure API Management Integration**                         | **To Be Completed** | Integration with Azure API Management for enhanced security, analytics, and monitoring of API endpoints.                                                              |

---

This table provides an overview of what has been built so far and outlines the remaining areas that need to be developed to fully implement the TPRM data model application. Let me know if you’d like to proceed with any specific component or if you have any questions regarding the scope!



tprm_webapp/
├── .env
├── requirements.txt
├── requirements-dev.txt
├── create_tables_sql.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── security.py
│   ├── monitoring/
│   │   └── azure_monitor.py
│   └── routers/
│       ├── __init__.py
│       ├── company.py
│       ├── assessments.py
│       ├── tasks.py
│       ├── scoring.py
│       ├── due_diligence.py
│       └── auth.py
└── (Optional) tests/   (for unit tests)
