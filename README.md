# Databricks Monthly Newsletter Workflow

This repository manages the Databricks monthly enablement newsletters with automatic deployment via AWS Amplify.

🌐 **Live Site**: [Databricks Newsletter Archive](https://main.amplifyapp.com/your-unique-url)

## 📋 Overview

- **Newsletter Files**: `January_Enablement_Newsletter.html`, `February_Enablement_Newsletter.html`, etc.
- **Landing Page**: `index.html` - Archive page with navigation to all newsletters
- **Hosting**: AWS Amplify with automatic deployments from GitHub
- **Repository**: https://github.com/jneil17/workshop_newsletter
- **Deployment**: Automatic on git push to `main` branch

## 🚀 Quick Deployment Workflow

The deployment process is now fully automated via AWS Amplify:

```bash
# 1. Edit newsletter file (e.g., February_Enablement_Newsletter.html)
# 2. Commit and push changes
git add .
git commit -m "Updated newsletter content - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# 3. AWS Amplify automatically builds and deploys! ✨
```

**That's it!** No manual deployment scripts needed.

## 📁 Project Structure

```
workshop_newsletter/
├── index.html                                   # Landing page - newsletter archive
├── Databricks_Monthly_Enablement_Newsletter.html # Main live newsletter (consistent URL)
├── February_Enablement_Newsletter.html         # February 2026 archive  
├── January_Enablement_Newsletter.html          # January 2026 archive
├── March_Enablement_Newsletter.html            # March 2026 future newsletter
├── April_Enablement_Newsletter.html            # April 2026 future newsletter
├── May_Enablement_Newsletter.html              # May 2026 future newsletter
├── amplify.yml                                 # AWS Amplify build configuration
├── README.md                                   # This file
├── .gitignore                                  # Git ignore rules
└── .github/
    └── copilot-instructions.md                 # Project documentation/context
```

## 🛠 AWS Amplify Setup (One-Time Configuration)

### Prerequisites
- AWS Account with Amplify access
- GitHub repository: https://github.com/jneil17/workshop_newsletter

### Setup Steps

1. **Connect to Amplify**
   - Log into AWS Console → Amplify
   - Click "Host web app" → GitHub
   - Select repository: `jneil17/workshop_newsletter`
   - Branch: `main`

2. **Build Configuration** 
   - Amplify will automatically detect `amplify.yml`
   - No additional build steps needed (static HTML files)
   - CDN resources: Tailwind CSS, Google Fonts, Font Awesome

3. **Domain Setup**
   - Amplify provides auto-generated domain
   - Optional: Configure custom domain
   - All newsletter files accessible at root level

4. **Environment Variables** (if needed)
   - None required for static HTML hosting

## 🎨 Newsletter Architecture

### Content Structure
- **Static HTML**: Self-contained newsletters with CDN-only resources
- **No Build Process**: Direct HTML serving, no compilation needed
- **Responsive Design**: Tailwind CSS with Databricks brand colors
- **Regional Events**: Integration with workshop and event data

### Brand Colors (Databricks)
```css
lava: { 500: '#FF5F46', 600: '#FF3621' }    /* Primary brand orange */
navy: { 800: '#1B3139', 900: '#0B2026' }    /* Dark text/backgrounds */  
oat: { light: '#F9F7F4', medium: '#EEEDE9' } /* Light backgrounds */
```

### HTML Best Practices
- Semantic HTML5 structure
- Proper heading hierarchy (h1 → h6)
- ARIA labels for accessibility
- Workshop weeks as `<section id="weekN">`
- Regional events grid with registration links

## 📝 Creating New Monthly Newsletters

### Monthly Workflow
1. **Edit Current Newsletter**: Update `Databricks_Monthly_Enablement_Newsletter.html` (main live file)
2. **Archive Previous**: Copy current to `[Month]_Enablement_Newsletter.html` for archival
3. **Update Content**: 
   - Change all month references in main file
   - Update workshop links and dates
   - Refresh regional events data
   - Update "Coming This Spring" preview section
4. **Test Links**: Verify all registration and workshop URLs
5. **Deploy**: Git commit + push → automatic Amplify deployment

### File Structure
- **`Databricks_Monthly_Enablement_Newsletter.html`** - Main live newsletter (consistent URL)
- **`February_Enablement_Newsletter.html`** - February 2026 archive
- **`January_Enablement_Newsletter.html`** - January 2026 archive
- **`index.html`** - Landing page with navigation to live + archive versions

### Benefits
- **Consistent URL**: `/.../Databricks_Monthly_Enablement_Newsletter.html` never changes
- **Archive Tracking**: Keep historical versions for reference
- **User Experience**: Bookmarked URLs always show latest content

### Link Styling Guidelines
- **Workshop links**: `text-lava-500 underline hover:text-lava-600`  
- **Event registration**: `bg-lava-500 text-white hover:bg-lava-600`
- **Dark backgrounds**: Use `text-lava-500` for visibility
- **Light backgrounds**: Use `text-lava-600` or `text-navy-800`

## 🔄 Rollback Procedures

### Quick Rollback
```bash
# Rollback to previous version
git log --oneline                                    # Find commit hash
git checkout [commit-hash] -- February_Enablement_Newsletter.html
git commit -m "Rollback newsletter to previous version"
git push origin main                                 # Triggers auto-redeploy
```

### Emergency Index Page Update
```bash
# Update landing page links or content
vim index.html
git add index.html
git commit -m "Updated newsletter archive landing page"
git push origin main
```

## 🚨 Troubleshooting

### Common Issues

**Amplify Build Fails**
- Check `amplify.yml` syntax
- Verify all referenced files exist
- Review build logs in AWS Amplify console

**Newsletter Links Broken**  
- Test all workshop registration URLs
- Verify event links are still active
- Check relative vs absolute paths

**CSS/Styling Issues**
- Confirm CDN resources loading (Tailwind, fonts)
- Check internet connectivity during build
- Verify Databricks brand color definitions

**Git Issues**
- Ensure GitHub repository is accessible
- Check git remote: `git remote -v`
- Verify Databricks pre-commit hooks pass

### Debug Commands
```bash
# Check git status
git status
git log --oneline -n 5

# Test AWS Amplify build locally (optional)
# No build process needed for static site

# Verify file structure
ls -la *.html
```

## 📚 Legacy Files (No Longer Used)

The following files are kept for reference but not used in Amplify deployment:
- `deploy.sh` - Original January-specific S3 deployment
- `deploy-new.sh` - Generic S3 deployment script
- `feb_file.md` - Workshop data source (integrated into February newsletter)
- `Sheet34.html` - Regional events source data

## 🔗 Useful Resources

- **AWS Amplify Console**: Monitor deployments and build logs
- **GitHub Repository**: https://github.com/jneil17/workshop_newsletter
- **Tailwind CSS Docs**: https://tailwindcss.com/docs (for styling updates)
- **Databricks Brand Guidelines**: Use defined color palette consistently

## 📞 Support

For deployment issues or questions:
- Check build logs in AWS Amplify Console  
- Review commit history for recent changes
- Verify all workshop links are accessible
- Test responsive design across devices

---

**🎯 Remember**: The goal is a simple, automated workflow where editing a newsletter and pushing to git immediately updates the live site!