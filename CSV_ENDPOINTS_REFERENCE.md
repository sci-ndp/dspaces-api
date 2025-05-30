# DSpaces CSV API - Quick Reference

## 📚 Complete API Documentation

**For comprehensive endpoint documentation, request/response schemas, and interactive testing:**

**➡️ [http://localhost:8001/docs](http://localhost:8001/docs) - FastAPI Auto-Generated Swagger UI**

The Swagger UI provides:

- ✅ Complete endpoint specifications
- ✅ Request/response models with validation
- ✅ Interactive API testing interface
- ✅ Real-time parameter documentation
- ✅ Authentication requirements
- ✅ HTTP status codes and error responses

## 🔧 Practical Usage Patterns

**For real-world workflows, integration examples, and best practices:**

**➡️ [CSV_WORKFLOWS_AND_INTEGRATION.md](CSV_WORKFLOWS_AND_INTEGRATION.md) - Workflows & Integration Guide**

## Quick Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | API health check |
| `/dspaces/ingest/{dataset_type}` | POST | Ingest CSV datasets |
| `/dspaces/retrieve/{dataset_type}/{namespace}` | GET | Retrieve full datasets |
| `/dspaces/ingest/{dataset_type}/sample` | GET | Preview CSV samples |
| `/dspaces/retrieve/{dataset_type}/{namespace}/filter` | GET/POST | Filter data with criteria |
| `/dspaces/retrieve/{dataset_type}/{namespace}/aggregate` | POST | Statistical aggregations |
| `/dspaces/retrieve/{dataset_type}/{namespace}/available-filters` | GET | Discover filter options |

## Getting Started

1. **Check API Status**: `GET /health`
2. **Preview Your Data**: `GET /dspaces/ingest/{dataset_type}/sample`
3. **Ingest Data**: `POST /dspaces/ingest/{dataset_type}`
4. **Explore Filters**: `GET /dspaces/retrieve/{dataset_type}/{namespace}/available-filters`
5. **Query Data**: Use filter and aggregate endpoints

## Documentation Structure

- **[Swagger UI](http://localhost:8001/docs)** - Complete technical API reference
- **[CSV_WORKFLOWS_AND_INTEGRATION.md](CSV_WORKFLOWS_AND_INTEGRATION.md)** - Practical usage patterns and code examples
- **[CSV_API_DEVELOPER_GUIDE.md](CSV_API_DEVELOPER_GUIDE.md)** - Programming integration guide
