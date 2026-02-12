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

## Current Status (December 2024 - Post CSV Alignment)

### CSV Data Source Authority
- **Source File**: `databricks_workshops_EST.csv` with 40 verified workshops
- **Date Range**: February 17 - April 30, 2026 (series ends April 30th)
- **Distribution**: February (8), March (14), April (18), May (0)
- **Critical Discovery**: May workshops in original newsletters were completely fake/non-existent

### Newsletter Implementation Status
- **February Newsletter** (Main): ✅ **100% COMPLETE** (8/8 workshops from CSV)
  - File: `Databricks_Monthly_Enablement_Newsletter.html`
  - Accuracy: All dates, times, and content match CSV source
  - Status: Live and verified accurate

- **March Newsletter**: 🟡 **PARTIAL** (1/14 workshops implemented)
  - File: `March_Enablement_Newsletter.html` 
  - Remaining: 13 workshops need CSV alignment
  - Priority: Medium (incremental improvement)

- **April Newsletter**: 🟡 **PARTIAL** (1/18 workshops implemented)
  - File: `April_Enablement_Newsletter.html`
  - Remaining: 17 workshops need CSV alignment  
  - Priority: Medium (incremental improvement)

- **May Newsletter**: ✅ **COMPLETE REWRITE** (0/0 workshops - correct)
  - File: `May_Enablement_Newsletter.html`
  - Status: Converted to "FY26 Series Complete" page
  - Features: Workshop recap, learning resources, FY27 signup

### Critical Fixes Completed
- ✅ **Fake Workshop Removal**: Eliminated all non-existent May workshops
- ✅ **Landing Page Accuracy**: Updated to show series concludes April 30, 2026
- ✅ **February Precision**: 100% alignment with CSV data (Feb 17-27 schedule)
- ✅ **Series End Communication**: Clear messaging that spring series concludes in April
- ✅ **Alternative Resources**: May newsletter provides Academy/community links

### Technical Infrastructure
- **GitHub**: https://github.com/jneil17/workshop_newsletter (public, auto-deploy enabled)
- **AWS Amplify**: Connected with automatic deployments from GitHub main branch
- **Domain**: dbx4startups.com (live and working)
- **Google Calendar**: Workshop calendar integrated on landing page
- **Deployment**: Automatic via `git push origin main`

### Files Status
- **Core Files**: 
  - `databricks_workshops_EST.csv` (authoritative source - 40 workshops)
  - `Databricks_Monthly_Enablement_Newsletter.html` (February - 100% accurate)
  - `index.html` (landing page - updated for April series end)
  - `May_Enablement_Newsletter.html` (series completion page)
- **Partial Files**: 
  - `March_Enablement_Newsletter.html` (needs 13 more workshops)
  - `April_Enablement_Newsletter.html` (needs 17 more workshops)
- **Configuration**: 
  - `amplify.yml`, `deploy-new.sh` (legacy), `.github/copilot-instructions.md`

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

## Recent Data Validation (December 2024)

### Critical Issues Discovered & Resolved
1. **Fake Workshop Problem**: Original May newsletter contained completely fictitious workshops
   - **Impact**: Misleading users about non-existent events
   - **Resolution**: Complete rewrite to "FY26 Series Complete" message
   
2. **CSV Misalignment**: Newsletters had incorrect dates/incomplete coverage
   - **Root Cause**: Manual editing without CSV verification
   - **Resolution**: Systematic CSV-based corrections for February (100% complete)

3. **Series End Confusion**: Landing page implied workshops continued beyond April
   - **Impact**: User expectations not aligned with actual schedule
   - **Resolution**: Clear April 30th end date messaging

### Validation Commands Used
```bash
# Verify CSV workshop counts
grep -c "^[^,]*,02/.*/2026" databricks_workshops_EST.csv  # February: 8
grep -c "^[^,]*,03/.*/2026" databricks_workshops_EST.csv  # March: 14  
grep -c "^[^,]*,04/.*/2026" databricks_workshops_EST.csv  # April: 18

# Check newsletter implementations
grep -c "02/.*2026.*EST" Databricks_Monthly_Enablement_Newsletter.html  # 8 (complete)
grep -c "03/.*2026.*EST" March_Enablement_Newsletter.html  # 1 (partial)
grep -c "04/.*2026.*EST" April_Enablement_Newsletter.html  # 1 (partial)
```

### Lessons Learned
- **Always verify against CSV source** before newsletter updates
- **Template copying can propagate errors** - validate each month independently  
- **User communication** - clearly state series end dates
- **Systematic approach** needed for multi-file consistency

## Monthly Newsletter Update Workflow (Updated)

### CSV-First Approach (REQUIRED):
1. **Verify CSV Data**: Always check `databricks_workshops_EST.csv` for authoritative workshop list
2. **Count Verification**: Use grep commands to verify workshop counts per month
3. **Date Validation**: Ensure newsletter dates exactly match CSV entries
4. **Series Boundaries**: Check CSV for actual start/end dates (no assumptions)

### For New Month Updates:
1. **Check CSV First**: Verify workshops exist for target month
2. **Archive Current**: Copy main newsletter to monthly archive
3. **CSV-Based Updates**: Use CSV data as single source of truth 
4. **Cross-Validation**: Verify newsletter counts match CSV counts
5. **Landing Page**: Update to reflect current month and series status
6. **Deploy & Verify**:
   ```bash
   git add .
   git commit -m "[Month] newsletter update - CSV verified - $(date '+%Y-%m-%d %H:%M:%S')"
   git push origin main
   ```

## Site Structure Summary
- **Live Domain**: dbx4startups.com
- **Main Newsletter**: `/Databricks_Monthly_Enablement_Newsletter.html` (consistent URL)
- **Landing Page**: `/` (index.html with full navigation and calendar)
- **Archives**: `/[Month]_Enablement_Newsletter.html` (historical versions)
- **Future Previews**: Available for planning and user engagement
- **Google Calendar**: Embedded for real-time workshop schedules
- **Responsive**: Optimized for all device sizes with Databricks branding