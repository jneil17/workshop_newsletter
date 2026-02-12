# Copilot Instructions for Databricks Newsletter Workflow

## Project Overview
This is a **monthly newsletter deployment system** for Databricks Customer Enablement. The core workflow is:
1. Edit monthly newsletter file (e.g., `February_Enablement_Newsletter.html`)
2. Run `./deploy-new.sh` to deploy changes to S3 and backup to GitHub  
3. Newsletter goes live at https://databricks-monthly-workshops-newsletter.s3.us-east-1.amazonaws.com/February_Enablement_Newsletter.html

**Evolution**: System upgraded from January-specific to reusable monthly infrastructure with generic bucket naming.

## Key Architecture

### Newsletter Files
- `January_Enablement_Newsletter.html` - Original January 2026 newsletter (843 lines) 
- `February_Enablement_Newsletter.html` - February 2026 newsletter with enhanced workshop content and regional events (950+ lines)
- Uses **CDN-only approach**: Tailwind CSS, Google Fonts, Font Awesome - no build process
- Self-contained styling with custom Databricks brand colors in `<script>` tag

### Content Integration 
- `feb_file.md` - Workshop links for FY26 (8 workshop URLs)
- `Sheet34.html` - Regional events data (March-May 2026 events)
- **Workshop Structure**: Each workshop week is semantically structured as `<section id="weekN">`
- **Regional Events**: Grid-based layout with clickable registration links and location details

### Deployment Pipeline
- `deploy.sh` - Original January-specific deployment script 
- `deploy-new.sh` - **Enhanced generic deployment script** for any monthly newsletter
- **Critical order**: Git commit → S3 bucket creation → S3 upload → GitHub push
- Built-in validation: checks AWS CLI, file existence, and Git state
- Auto-detects newsletter filename, supports bucket auto-creation
- Colorized output with emoji for clear status feedback

### AWS Integration
- **Current Target**: `s3://databricks-january-workshops/` bucket (legacy)
- **New Target**: `s3://databricks-monthly-workshops-newsletter/` bucket (reusable for all months)
- **Auth**: `jneil_developer` IAM user with limited S3 permissions (can access specific buckets but cannot create new buckets)
- **Region**: `us-east-1` (hardcoded in workflow)
- Sets proper `content-type: text/html` and cache headers
- **Permission Note**: Bucket creation requires admin privileges - coordinate with AWS admin for new bucket setup

## Development Patterns

### Color System (Databricks Brand)
```html
lava: { 500: '#FF5F46', 600: '#FF3621' }    // Primary brand
navy: { 800: '#1B3139', 900: '#0B2026' }    // Dark text/backgrounds  
oat: { light: '#F9F7F4', medium: '#EEEDE9' } // Light backgrounds
```

### HTML Structure Conventions
- **Semantic sections**: Each workshop week is `<section id="weekN">`
- **Brand consistency**: `.brand-gradient`, `.btn-lava` classes
- **Responsive design**: Tailwind responsive classes (`md:` prefixes)
- **Accessibility**: Proper ARIA labels and semantic markup

### Git Workflow
- **Auto-timestamping**: Commits use `$(date '+%Y-%m-%d %H:%M:%S')` format
- **Rollback support**: `git log --oneline` to find commits, edit file, re-deploy
- **Secret scanning**: Databricks git hooks prevent credential commits (use `# gitleaks:allow` when needed)

## Critical Commands

### Primary Workflow
```bash
./deploy.sh       # January-specific deployment (legacy)
./deploy-new.sh   # Generic monthly deployment (recommended for reuse)
```

### Manual Operations
```bash
# Deploy to generic bucket
aws s3 cp February_Enablement_Newsletter.html s3://databricks-monthly-workshops-newsletter/February_Enablement_Newsletter.html --content-type "text/html"

# Deploy to January bucket (legacy)
aws s3 cp January_Enablement_Newsletter.html s3://databricks-january-workshops/January_Enablement_Newsletter.html --content-type "text/html"

# Rollback pattern (works with any monthly file)
git checkout [commit-hash] -- February_Enablement_Newsletter.html
./deploy-new.sh
```

### Verification
```bash
aws sts get-caller-identity  # Check AWS auth
aws s3 ls s3://databricks-january-workshops/  # Test bucket access
```

## When Making Changes

1. **Always test AWS permissions first** if deployment fails
2. **Use semantic HTML** - newsletter uses proper heading hierarchy and sections
3. **Maintain brand colors** - stick to the defined lava/navy/oat palette
4. **Update month/dates** consistently throughout the document
5. **Test responsive design** - heavy use of Tailwind responsive utilities
6. **Verify public URL** after deployment to ensure changes are live
7. **Link visibility** - Use `text-lava-500 underline` for clickable links on dark backgrounds
8. **Workshop integration** - Reference `feb_file.md` for current FY26 workshop URLs
9. **Regional events** - Check `Sheet34.html` for latest event data and registration links

## Environment Dependencies
- **AWS CLI** configured with `jneil_developer` credentials  
- **Git** with Databricks pre-commit hooks enabled
- **Internet access** for CDN resources (Tailwind, fonts, icons)

## Current Status (February 2026)
- **February Newsletter**: Complete with 8 FY26 workshop links and regional events
- **GitHub**: Changes successfully pushed to https://github.com/jneil17/workshop_newsletter
- **S3 Bucket**: Needs `databricks-monthly-workshops-newsletter` bucket created by AWS admin
- **Deployment**: Ready to deploy once bucket exists
- **Files Created**: 
  - `February_Enablement_Newsletter.html` (950+ lines)
  - `deploy-new.sh` (enhanced deployment script)
  - `feb_file.md`, `Sheet34.html` (source data files)