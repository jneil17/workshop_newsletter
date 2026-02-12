# Copilot Instructions for Databricks Newsletter Workflow

## Project Overview
This is a **monthly newsletter deployment system** for Databricks Customer Enablement. The core workflow is:
1. Edit main newsletter file (`Databricks_Monthly_Enablement_Newsletter.html`)
2. Commit and push changes to GitHub
3. AWS Amplify automatically deploys from git repository
4. Newsletter goes live via Amplify hosting with consistent URL

**Evolution**: System upgraded from manual S3 deployment to automated AWS Amplify deployment with git integration. Uses consistent filename for predictable URLs.

## Key Architecture

### Newsletter Files
- `Databricks_Monthly_Enablement_Newsletter.html` - **Main live newsletter** with consistent URL (950+ lines)
- `February_Enablement_Newsletter.html` - February 2026 archive with enhanced workshop content and regional events
- `January_Enablement_Newsletter.html` - January 2026 archive (843 lines)
- `March_Enablement_Newsletter.html` - March 2026 future newsletter preview
- `April_Enablement_Newsletter.html` - April 2026 future newsletter preview  
- `May_Enablement_Newsletter.html` - May 2026 future newsletter preview
- Uses **CDN-only approach**: Tailwind CSS, Google Fonts, Font Awesome - no build process
- Self-contained styling with custom Databricks brand colors in `<script>` tag

### Content Integration 
- `feb_file.md` - Workshop links for FY26 (8 workshop URLs)
- `Sheet34.html` - Regional events data (March-May 2026 events)
- **Workshop Structure**: Each workshop week is semantically structured as `<section id="weekN">`
- **Regional Events**: Grid-based layout with clickable registration links and location details

### Deployment Pipeline
- **Automatic Deployment**: AWS Amplify connected to GitHub repository
- **Workflow**: Edit files → Git commit → Git push → Amplify auto-deploys
- **Legacy Scripts**: `deploy.sh` and `deploy-new.sh` (no longer needed with Amplify)
- **Repository**: https://github.com/jneil17/workshop_newsletter
- Built-in CI/CD with Amplify's build and hosting infrastructure

### AWS Integration
- **Hosting**: AWS Amplify with automatic deployments from GitHub
- **Domain**: dbx4startups.com (custom domain configured in Amplify)
- **Legacy S3 Buckets**: `databricks-january-workshops/` and `databricks-monthly-workshops-newsletter/` (no longer used)
- **Build**: Static site hosting - no build process required (CDN-only resources)
- **Auth**: Managed through Amplify service, no manual AWS CLI needed

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
git add .
git commit -m "Newsletter updates - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main     # Triggers automatic Amplify deployment
```

### Legacy Operations (No Longer Used)
```bash
./deploy.sh       # Old January-specific deployment 
./deploy-new.sh   # Old generic deployment script
```

### Rollback Operations
```bash
# Rollback pattern (works with any monthly file)
git checkout [commit-hash] -- February_Enablement_Newsletter.html
git commit -m "Rollback newsletter to previous version"
git push origin main     # Triggers Amplify redeploy
```

### Verification
```bash
aws sts get-caller-identity  # Check AWS auth
aws s3 ls s3://databricks-january-workshops/  # Test bucket access
```

## Amplify Setup (One-Time Configuration)
1. **Connect Repository**: Link https://github.com/jneil17/workshop_newsletter to AWS Amplify
2. **Build Settings**: No build process needed - static HTML files
3. **Environment**: Production branch = `main`
4. **Domain**: dbx4startups.com (custom domain configured and working)

## When Making Changes

1. **Always test AWS permissions first** if deployment fails
2. **Use semantic HTML** - newsletter uses proper heading hierarchy and sections
3. **Maintain brand colors** - stick to the defined lava/navy/oat palette
4. **Update month/dates** consistently throughout the document
5. **Test responsive design** - heavy use of Tailwind responsive utilities
6. **Verify public URL** after deployment to ensure changes are live at dbx4startups.com
7. **Link visibility** - Use `text-lava-500 underline` for clickable links on dark backgrounds
8. **Workshop integration** - Reference `feb_file.md` for current FY26 workshop URLs
9. **Regional events** - Check `Sheet34.html` for latest event data and registration links

## Environment Dependencies
- **Git** with Databricks pre-commit hooks enabled
- **Internet access** for CDN resources (Tailwind, fonts, icons)

## Current Status (February 2026)
- **February Newsletter**: Complete with 8 FY26 workshop links and regional events
- **GitHub**: Changes successfully pushed to https://github.com/jneil17/workshop_newsletter
- **Repository**: Public (required for AWS Amplify free tier)
- **AWS Amplify**: Connected to GitHub repository with auto-deployment
- **Domain**: dbx4startups.com (live and working)
- **Deployment**: Automatic via git push once Amplify is configured
- **Future Newsletters**: March, April, May 2026 newsletters created with preview functionality
- **Google Calendar**: Workshop calendar integrated on landing page
- **Files Created**: 
  - `Databricks_Monthly_Enablement_Newsletter.html` (main live newsletter)
  - `February_Enablement_Newsletter.html` (950+ lines)
  - `March_Enablement_Newsletter.html`, `April_Enablement_Newsletter.html`, `May_Enablement_Newsletter.html` (future newsletters)
  - `index.html` (professional landing page with calendar integration)
  - `amplify.yml` (AWS Amplify build configuration)
  - `deploy-new.sh` (enhanced deployment script - legacy)
  - `feb_file.md`, `Sheet34.html` (source data files)

## Landing Page Features
- **Professional branding** with Databricks color scheme
- **Current newsletter highlight** with main call-to-action
- **Archive section** for historical newsletters (January, February)
- **Google Calendar embed** for live workshop schedule
- **Coming Soon section** with future newsletter previews (March, April, May)
- **Responsive design** optimized for mobile and desktop

## Troubleshooting (Common Issues)
- **Amplify "Repository not found" error**: Repository must be PUBLIC for Amplify free tier
  - Fix: `gh repo edit jneil17/workshop_newsletter --visibility public --accept-visibility-change-consequences`
- **Amplify "Base Directory not specified" error**: amplify.yml missing baseDirectory
  - Fix: Add `baseDirectory: '.'` in artifacts section of amplify.yml
- **Auth issues**: Ensure GitHub CLI is authenticated as correct user (`gh auth switch --user jneil17`)

## Monthly Newsletter Update Workflow

### For New Month (e.g., March 2026):
1. **Archive Current**: Copy `Databricks_Monthly_Enablement_Newsletter.html` to `February_Enablement_Newsletter.html`
2. **Edit Main File**: Update `Databricks_Monthly_Enablement_Newsletter.html` with March content
3. **Update Landing Page**: Modify `index.html` to reflect new current month in hero section
4. **Test Links**: Verify all workshop and registration URLs
5. **Deploy**: 
   ```bash
   git add .
   git commit -m "March 2026 newsletter update - $(date '+%Y-%m-%d %H:%M:%S')"
   git push origin main
   ```
6. **Verify**: Check dbx4startups.com for live updates

### Content Update Guidelines:
- **Workshop Links**: Use current FY workshop URLs from latest source data
- **Regional Events**: Update with current quarter's events and registration links
- **Coming Soon**: Adjust preview section for next 3 months
- **Meta Tags**: Update month references in `<title>` and SEO tags
- **Calendar**: Google Calendar updates automatically, no manual changes needed

## Site Structure Summary
- **Live Domain**: dbx4startups.com
- **Main Newsletter**: `/Databricks_Monthly_Enablement_Newsletter.html` (consistent URL)
- **Landing Page**: `/` (index.html with full navigation and calendar)
- **Archives**: `/[Month]_Enablement_Newsletter.html` (historical versions)
- **Future Previews**: Available for planning and user engagement
- **Google Calendar**: Embedded for real-time workshop schedules
- **Responsive**: Optimized for all device sizes with Databricks branding