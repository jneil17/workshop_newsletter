# January Enablement Newsletter Workflow

This repository manages the Databricks January Enablement Newsletter that is publicly available at:
**https://databricks-january-workshops.s3.us-east-1.amazonaws.com/January_Enablement_Newsletter.html**

## 📋 Overview

- **Source File**: `January_Enablement_Newsletter.html`
- **S3 Bucket**: `s3://databricks-january-workshops/`
- **GitHub Repository**: Backup and version control
- **Public URL**: https://databricks-january-workshops.s3.us-east-1.amazonaws.com/January_Enablement_Newsletter.html

## 🚀 Quick Deploy

After making changes to the HTML file, simply run:

```bash
./deploy.sh
```

This script will:
1. ✅ Commit your changes to Git
2. ☁️ Upload the file to S3
3. 📤 Push changes to GitHub

## 🛠 Setup Requirements

### AWS CLI Configuration
Make sure you have AWS CLI installed and configured with appropriate permissions:

```bash
# Install AWS CLI (if not already installed)
pip install awscli

# Configure AWS credentials
aws configure
```

**AWS Credentials Setup:**
1. **Access Key ID**: `AKIAZI2LGMDC2NLULV4E` (for jneil_developer user) # gitleaks:allow
2. **Secret Access Key**: [Configured separately]
3. **Region**: `us-east-1`
4. **Output Format**: `json`

**Required IAM Policy for `jneil_developer` user:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::databricks-january-workshops/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::databricks-january-workshops"
        }
    ]
}
```

**Verify Setup:**
```bash
# Check AWS identity
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://databricks-january-workshops/
```

### Git Configuration
Ensure your Git is configured:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@databricks.com"
```

## 📝 Workflow Steps

### 1. Make Changes
Edit the `January_Enablement_Newsletter.html` file with your updates.

### 2. Deploy
Run the deployment script:
```bash
./deploy.sh
```

### 3. Verify
Check the live site: https://databricks-january-workshops.s3.us-east-1.amazonaws.com/January_Enablement_Newsletter.html

## 🔄 Manual Commands (if needed)

### Deploy to S3 only:
```bash
aws s3 cp January_Enablement_Newsletter.html s3://databricks-january-workshops/January_Enablement_Newsletter.html --content-type "text/html"
```

### Commit and push to GitHub only:
```bash
git add January_Enablement_Newsletter.html
git commit -m "Update newsletter: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
```

## 📚 File Structure

```
workshop_newsletter/
├── January_Enablement_Newsletter.html  # Main newsletter file
├── deploy.sh                          # Deployment script
└── README.md                          # This file
```

## 🔧 Troubleshooting

### AWS Permissions
If you get permission errors, ensure your AWS credentials have access to the S3 bucket.

### Git Push Issues
If GitHub push fails, you may need to set up authentication:
```bash
# For SSH (recommended)
git remote set-url origin git@github.com:john-neil_data/workshop_newsletter.git

# For HTTPS with token
git remote set-url origin https://[token]@github.com/john-neil_data/workshop_newsletter.git
```

### Rollback Changes
To rollback to a previous version:
```bash
# View commit history
git log --oneline

# Revert to specific commit
git checkout [commit-hash] -- January_Enablement_Newsletter.html

# Deploy the reverted version
./deploy.sh
```

## 🎯 Best Practices

1. **Always test locally** before deploying
2. **Use meaningful commit messages** when making changes
3. **Check the live site** after deployment
4. **Keep regular backups** (GitHub serves as our backup)
5. **Document major changes** in commit messages