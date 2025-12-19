# Copilot Instructions for Databricks Newsletter Workflow

## Project Overview
This is a **single-page newsletter deployment system** for Databricks Customer Enablement. The core workflow is:
1. Edit `January_Enablement_Newsletter.html` (the main content file)
2. Run `./deploy.sh` to deploy changes to S3 and backup to GitHub
3. Newsletter goes live at https://databricks-january-workshops.s3.us-east-1.amazonaws.com/January_Enablement_Newsletter.html

## Key Architecture

### Single Source of Truth
- `January_Enablement_Newsletter.html` - Main newsletter file (919 lines of semantic HTML)
- Uses **CDN-only approach**: Tailwind CSS, Google Fonts, Font Awesome - no build process
- Self-contained styling with custom Databricks brand colors in `<script>` tag

### Deployment Pipeline
- `deploy.sh` - Atomic deployment script that handles Git + S3 in one command
- **Critical order**: Git commit → S3 upload → GitHub push
- Built-in validation: checks AWS CLI, file existence, and Git state
- Colorized output with emoji for clear status feedback

### AWS Integration
- **Target**: `s3://databricks-january-workshops/` bucket
- **Auth**: `jneil_developer` IAM user with specific S3 permissions
- **Region**: `us-east-1` (hardcoded in workflow)
- Sets proper `content-type: text/html` and cache headers

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
./deploy.sh  # Complete deployment (most common command)
```

### Manual Operations
```bash
# Deploy to S3 only
aws s3 cp January_Enablement_Newsletter.html s3://databricks-january-workshops/January_Enablement_Newsletter.html --content-type "text/html"

# Rollback pattern
git checkout [commit-hash] -- January_Enablement_Newsletter.html
./deploy.sh
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

## Environment Dependencies
- **AWS CLI** configured with `jneil_developer` credentials  
- **Git** with Databricks pre-commit hooks enabled
- **Internet access** for CDN resources (Tailwind, fonts, icons)