# Beta Testing Guide - LeanConstruction AI Phase 2

## Overview

Welcome to the LeanConstruction AI Beta Testing Program! This guide will help beta testers evaluate our Phase 2 AI-powered construction analytics platform.

### Phase 2 Features Under Test

1. **Computer Vision Progress Monitoring** - CNN-based site progress analysis
2. **Waste Detection (DOWNTIME)** - 8-type lean waste identification
3. **Predictive Analytics** - Schedule and cost forecasting
4. **Automated Reporting** - Multi-format construction reports

---

## Quick Start for Beta Testers

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-org/lean-construction.git
cd lean-construction

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/leanconstruction

# API Keys (optional for beta)
OPENAI_API_KEY=your_key_here

# ML Model Paths
MODEL_PATH=./models/
DATA_PATH=./data/

# Feature Flags for Beta
ENABLE_CV_PROGRESS=true
ENABLE_WASTE_DETECTION=true
ENABLE_FORECASTING=true
ENABLE_REPORTING=true
```

### 3. Running the Application

```bash
# Start the backend API
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Docker
docker-compose up -d
```

---

## Testing Each Module

### Module 1: Computer Vision Progress Monitoring

#### What It Does
- Analyzes construction site images to detect progress stages
- Identifies 13 construction stages from site preparation to completion
- Provides confidence scores for stage classification

#### How to Test

**API Endpoint:** `POST /api/v1/ml/analyze-progress`

```bash
# Upload an image for analysis
curl -X POST "http://localhost:8000/api/v1/ml/analyze-progress" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@site_image.jpg" \
  -F "project_id=BETA-001"
```

**Expected Response:**
```json
{
  "status": "success",
  "analysis": {
    "detected_stage": "structural",
    "confidence": 0.87,
    "stage_probabilities": {
      "foundation": 0.05,
      "structural": 0.87,
      "mep_rough_in": 0.08
    },
    "detected_activities": ["steel_erection", "concrete_forming"],
    "progress_estimate": 35.5
  }
}
```

#### Test Scenarios

| Scenario | Input | Expected Result |
|----------|-------|-----------------|
| Foundation stage | Image of foundation work | `detected_stage: "foundation"` |
| Structural stage | Image of steel/framing | `detected_stage: "structural"` |
| Interior finishes | Image of drywall/paint | `detected_stage: "interior_finishes"` |
| Low quality image | Blurry image | Lower confidence score (<0.6) |

#### Feedback Points
- [ ] Accuracy of stage detection
- [ ] Relevance of detected activities
- [ ] Response time performance
- [ ] Handling of edge cases (night photos, partial views)

---

### Module 2: Waste Detection (DOWNTIME Framework)

#### What It Does
Analyzes project data to identify the 8 lean construction wastes:

| Waste Type | Description |
|------------|-------------|
| **D**efects | Quality issues requiring rework |
| **O**verproduction | Producing more than needed |
| **W**aiting | Idle time waiting for resources |
| **N**on-utilized Talent | Underused worker skills |
| **T**ransportation | Unnecessary material movement |
| **I**nventory | Excess materials/supplies |
| **M**otion | Unnecessary worker movement |
| **E**xtra Processing | Over-engineering, redundant work |

#### How to Test

**API Endpoint:** `POST /api/v1/ml/analyze-waste`

```bash
curl -X POST "http://localhost:8000/api/v1/ml/analyze-waste" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "BETA-001",
    "data": {
      "schedule_data": {...},
      "resource_data": {...},
      "quality_data": {...}
    }
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "analysis": {
    "overall_waste_score": 0.35,
    "health_status": "moderate",
    "detected_wastes": {
      "waiting": {
        "detected": true,
        "severity_score": 0.45,
        "estimated_cost_impact": 15000,
        "indicators": ["idle_workers", "material_delays"]
      },
      "defects": {
        "detected": true,
        "severity_score": 0.30,
        "estimated_cost_impact": 8000,
        "indicators": ["rework_needed"]
      }
    },
    "priority_actions": [
      {
        "waste_type": "waiting",
        "action": "Review material delivery schedule",
        "priority": "high"
      }
    ]
  }
}
```

#### Test Data Templates

Use these templates to test different scenarios:

**Healthy Project:**
```json
{
  "rework_hours": 10,
  "idle_time_hours": 5,
  "material_waste_pct": 2,
  "schedule_variance_days": 1
}
```

**Problem Project:**
```json
{
  "rework_hours": 100,
  "idle_time_hours": 80,
  "material_waste_pct": 15,
  "schedule_variance_days": 20
}
```

#### Feedback Points
- [ ] Accuracy of waste detection
- [ ] Relevance of cost impact estimates
- [ ] Quality of recommended actions
- [ ] Ease of understanding waste categories

---

### Module 3: Predictive Analytics (Schedule & Cost)

#### What It Does
- **Schedule Forecasting**: LSTM-based prediction of completion dates
- **Cost Forecasting**: Ensemble model predicting final project cost
- **Risk Assessment**: Combined risk level determination

#### How to Test

**API Endpoint:** `POST /api/v1/ml/forecast`

```bash
curl -X POST "http://localhost:8000/api/v1/ml/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "BETA-001",
    "historical_data": {
      "progress_series": [...],
      "cost_series": [...],
      "worker_counts": [...]
    },
    "project_info": {
      "budget": 10000000,
      "planned_duration": 365,
      "days_elapsed": 120
    }
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "forecast": {
    "schedule_forecast": {
      "predicted_completion_date": "2025-06-15",
      "schedule_variance_days": 12,
      "confidence_level": 0.85,
      "confidence_interval": {
        "lower": "2025-06-01",
        "upper": "2025-06-29"
      }
    },
    "cost_forecast": {
      "predicted_final_cost": 10250000,
      "budget_variance_percentage": 2.5,
      "cost_at_completion": 10320000,
      "confidence_interval": {
        "lower": 9800000,
        "upper": 10700000
      }
    },
    "combined_risk_level": "medium",
    "recommendations": [
      "Monitor critical path activities closely",
      "Review contingency allocation"
    ]
  }
}
```

#### Test Scenarios

| Scenario | Configuration | Expected Risk Level |
|----------|---------------|---------------------|
| On-track project | Low variance | `low` |
| Minor delays | 5-10 day variance | `medium` |
| Significant issues | >15 day variance, >10% cost overrun | `high` |

#### Feedback Points
- [ ] Accuracy of completion date predictions
- [ ] Reliability of cost estimates
- [ ] Appropriateness of risk levels
- [ ] Usefulness of confidence intervals

---

### Module 4: Automated Reporting

#### What It Does
Generates comprehensive construction reports in multiple formats:
- JSON (for API consumption)
- HTML (for web display)
- Markdown (for documentation)

#### Report Types

| Type | Sections Included | Use Case |
|------|-------------------|----------|
| Daily | Progress, Safety | Daily standup |
| Weekly | Progress, Waste, Safety, 5S | Weekly review |
| Monthly | All sections + Forecast | Monthly reporting |
| Executive | Progress, Forecast | Management summary |
| Comprehensive | All sections | Full analysis |

#### How to Test

**API Endpoint:** `POST /api/v1/reports/generate`

```bash
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "BETA-001",
    "report_type": "weekly",
    "output_format": "html"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "report": {
    "metadata": {
      "report_id": "RPT-20241209-0001",
      "report_type": "weekly",
      "project_name": "City Center Tower"
    },
    "executive_summary": {
      "overall_status": "good",
      "narrative": "Project is on track..."
    },
    "sections": [...],
    "html_content": "<!DOCTYPE html>..."
  }
}
```

#### Feedback Points
- [ ] Clarity of executive summary
- [ ] Completeness of sections
- [ ] Visual appeal of HTML output
- [ ] Relevance of recommendations
- [ ] Accuracy of metrics

---

## Feedback Submission

### Feedback Categories

1. **Accuracy** - How accurate are the AI predictions?
2. **Usability** - How easy is the system to use?
3. **Performance** - How fast are response times?
4. **Relevance** - How relevant are recommendations?
5. **Integration** - How well does it fit your workflow?

### Feedback Form

Please submit feedback using the following template:

```markdown
## Beta Feedback Report

**Company:** [Your Company Name]
**Tester:** [Your Name]
**Date:** [Date]
**Module Tested:** [CV/Waste/Forecast/Reporting]

### Test Environment
- Operating System:
- Browser/Client:
- Project Size:

### Test Results

#### Accuracy Rating (1-5): ___
Comments:

#### Usability Rating (1-5): ___
Comments:

#### Performance Rating (1-5): ___
Comments:

### Issues Encountered
1. [Description]
   - Steps to reproduce:
   - Expected behavior:
   - Actual behavior:

### Feature Requests
1. [Description]

### General Comments
[Your overall impressions]
```

### Submitting Feedback

- **Email:** beta-feedback@leanconstruction.ai
- **Portal:** https://beta.leanconstruction.ai/feedback
- **GitHub Issues:** For bug reports and technical issues

---

## Known Limitations (Beta)

1. **Computer Vision**
   - Best performance with well-lit daytime images
   - Single image analysis (no video yet)
   - US-style construction practices primarily

2. **Waste Detection**
   - Requires structured data input
   - Some waste types need more training data

3. **Forecasting**
   - Accuracy improves with historical data
   - Minimum 30 days history recommended

4. **Reporting**
   - PDF export not yet available
   - Chart rendering in HTML beta

---

## Support

### Beta Support Channels

- **Slack:** #beta-testers channel
- **Email:** support@leanconstruction.ai
- **Documentation:** https://docs.leanconstruction.ai

### Office Hours

Weekly beta tester calls:
- **When:** Thursdays 2:00 PM EST
- **Where:** Zoom (link in Slack)
- **What:** Q&A, demos, feedback discussion

---

## Timeline

| Phase | Dates | Focus |
|-------|-------|-------|
| Beta 1 | Weeks 1-2 | Core functionality testing |
| Beta 2 | Weeks 3-4 | Integration testing |
| Beta 3 | Weeks 5-6 | Performance & scale testing |
| GA Prep | Weeks 7-8 | Final fixes, documentation |

---

Thank you for participating in our beta program! Your feedback is invaluable in making LeanConstruction AI the best tool for the construction industry.