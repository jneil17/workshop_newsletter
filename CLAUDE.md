# CLAUDE.md - Workshop Newsletter Project Context

## Project Overview

This is a **monthly newsletter deployment system** for Databricks Customer Enablement workshops. The project maintains synchronized workshop information across multiple formats and serves a live website with automated deployments.

### Key Information
- **Live Domain**: [dbx4startups.com](https://dbx4startups.com)
- **Deployment**: AWS Amplify with automatic deployments from GitHub main branch
- **Repository**: https://github.com/jneil17/workshop_newsletter
- **Framework**: Static HTML with CDN-based resources (Tailwind CSS, Google Fonts)

## Architecture & Data Flow

### Single Source of Truth
- **`databricks_workshops_EST.csv`** - Authoritative workshop schedule
- Contains 40+ workshops from February-April 2026
- All newsletter HTML files should sync with this CSV data

### File Structure
```
├── databricks_workshops_EST.csv           # Master workshop data
├── Databricks_Monthly_Enablement_Newsletter.html  # Main live newsletter
├── [Month]_Enablement_Newsletter.html     # Monthly archives
├── index.html                            # Landing page with navigation
├── update-framework.py                   # Automated sync tool
└── .github/copilot-instructions.md       # Comprehensive documentation
```

## Recent Updates (February 2026)

### End-to-End AI Workshop Sync Issue
**Issue Identified**: The "End-to-End AI on Databricks" workshop descriptions were not synchronized with the official Databricks event page.

**Discrepancy Found**:
- **CSV/Newsletter (Old)**: Generic description about "end-to-end AI solution" and "reusable template"
- **Official Page**: Detailed content about AI agents, RAG, Vector Search, LangChain, specific presenters

### Changes Made

#### 1. CSV Updates (`databricks_workshops_EST.csv`)
Updated all 5 End-to-End AI workshop entries (rows 7, 11, 19, 27, 35) with detailed description:

```csv
"Walk through an end-to-end AI agent solution on Databricks. Build AI Agents with foundation LLMs, RAG, Vector Search, and PDF extraction using Unity Catalog functions, LangChain, and Databricks' built-in ai_parse_document function. Deploy real-time Q&A chatbots, evaluate agents with Mosaic AI Agent Evaluation and MLflow 3.0, and monitor live production behavior. Presenters: Rupal Gupta (Sr. Solutions Engineer) and Bhagyarshri Badgujar (Solutions Architect). Duration: 1.5 hrs."
```

#### 2. Newsletter HTML Updates
Updated the following files with new content structure:
- `Databricks_Monthly_Enablement_Newsletter.html`
- `March_Enablement_Newsletter.html`

**New HTML Structure**:
```html
<p class="text-gray-700 mb-4">
    Walk through an end-to-end AI agent solution on Databricks...
</p>
<div class="bg-oat-light rounded p-4 mb-4">
    <div class="font-semibold text-navy-800 mb-2">AI agent development features:</div>
    <ul class="text-sm text-gray-700 space-y-1">
        <li>• Build AI agents with foundation LLMs and RAG</li>
        <li>• PDF extraction using ai_parse_document function</li>
        <li>• Unity Catalog functions and Vector Search</li>
        <li>• Deploy real-time Q&A chatbots with LangChain</li>
        <li>• Evaluate with Mosaic AI Agent Evaluation and MLflow 3.0</li>
        <li>• Monitor live agents and production behavior</li>
    </ul>
</div>
<div class="bg-gray-50 rounded p-3 mb-4 text-sm">
    <div class="font-semibold text-navy-800 mb-1">Presenters:</div>
    <div class="text-gray-700">Rupal Gupta (Sr. Solutions Engineer) and Bhagyarshri Badgujar (Solutions Architect)</div>
</div>
```

#### 3. Framework Creation
Created `update-framework.py` for future automated synchronization between Databricks event pages and newsletter content.

## Data Issues Discovered

### January Newsletter Problem
⚠️ **CRITICAL**: `January_Enablement_Newsletter.html` contains **incorrect data**:
- Shows End-to-End AI workshop on "January 13, 2026"
- According to authoritative CSV, workshops don't start until February 17, 2026
- This is outdated/erroneous content that needs correction

## Workshop Categories & Branding

### Category System
- **MACHINE LEARNING** - Orange `bg-lava-600` badge (includes End-to-End AI)
- **GETTING STARTED** - Navy `bg-navy-800` badge (includes Intro to Databricks)
- **DATA ENGINEERING** - Blue badges
- **ANALYTICS & SQL** - Green badges
- **GOVERNANCE** - Purple badges

### Brand Colors
- **Lava**: #FF5F46, #FF3621
- **Navy**: #1B3139, #0B2026
- **Oat**: #F9F7F4, #EEEDE9

## End-to-End AI Workshop Details

### Schedule (All times 2:00 PM EST / 11:00 AM PT, 1.5 hours)
- February 24, 2026
- March 10, 2026
- March 24, 2026
- April 7, 2026
- April 21, 2026

### Key Technologies Covered
- Retrieval Augmented Generation (RAG)
- Vector Search
- LangChain
- Unity Catalog functions
- Mosaic AI Agent Evaluation
- MLflow 3.0
- Lakehouse Applications
- ai_parse_document function

### Official Event Page
https://events.databricks.com/FY26-EV-AEB-Hands-on-Workshop-End-to-EndAI

## Maintenance Guidelines

### Content Updates
1. **Always use CSV as source of truth** for workshop data
2. **Verify against official Databricks event pages** before publishing
3. **Use update-framework.py** to check for discrepancies
4. **Maintain consistent HTML structure** across newsletter files

### Before Making Changes
1. **Create backups** using: `python update-framework.py --backup`
2. **Check all workshops** using: `python update-framework.py --check-all`
3. **Test locally** before pushing to main branch

### Deployment Process
1. Git push to main branch triggers automatic AWS Amplify deployment
2. Changes appear live at dbx4startups.com within minutes
3. Monitor deployment status in AWS console

## Future Improvements Needed

### Immediate
1. **Fix January newsletter** - Remove erroneous End-to-End AI workshop date
2. **Complete March/April newsletters** - Only 1/14 and 1/18 workshops implemented respectively
3. **Validate all workshop URLs** - Ensure all links are current and working

### Long-term
1. **Enhance update-framework.py** with HTML newsletter updating capability
2. **Add automated testing** for content synchronization
3. **Implement content validation** pipeline
4. **Create workshop change detection** system

## Contact & Context

This documentation was created in February 2026 following a user report that End-to-End AI workshop content was out of sync with official Databricks event pages. The synchronization process involved updating both CSV data and HTML newsletter files to match the detailed content found on the official event page.

For future maintenance, always verify workshop content against official Databricks event pages and use the provided update-framework.py tool to identify and resolve content discrepancies.