#!/bin/bash

# Deploy script for Monthly Enablement Newsletter
# This script uploads HTML newsletter files to S3 and commits changes to Git
# Usage: ./deploy.sh [newsletter_file.html]
# If no file is specified, it will deploy February_Enablement_Newsletter.html by default

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# S3 Configuration
S3_BUCKET="databricks-monthly-workshops-newsletter"
S3_REGION="us-east-1"

# Determine which file to deploy
NEWSLETTER_FILE=${1:-"February_Enablement_Newsletter.html"}

echo -e "${BLUE}📰 Deploying Monthly Enablement Newsletter...${NC}"
echo -e "${YELLOW}📄 File: ${NEWSLETTER_FILE}${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    exit 1
fi

# Check if the HTML file exists
if [ ! -f "$NEWSLETTER_FILE" ]; then
    echo -e "${RED}❌ ${NEWSLETTER_FILE} not found!${NC}"
    echo -e "${YELLOW}Available newsletter files:${NC}"
    ls *_Enablement_Newsletter.html 2>/dev/null || echo "  No newsletter files found"
    exit 1
fi

# Verify AWS credentials and S3 bucket access
echo -e "${YELLOW}🔐 Verifying AWS credentials...${NC}"
aws sts get-caller-identity > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'${NC}"
    exit 1
fi

# Check if S3 bucket exists, create if it doesn't
echo -e "${YELLOW}🪣 Checking S3 bucket...${NC}"
if ! aws s3 ls "s3://${S3_BUCKET}" > /dev/null 2>&1; then
    echo -e "${YELLOW}📦 Creating S3 bucket: ${S3_BUCKET}${NC}"
    
    # Create the bucket
    if [ "$S3_REGION" == "us-east-1" ]; then
        aws s3 mb "s3://${S3_BUCKET}"
    else
        aws s3 mb "s3://${S3_BUCKET}" --region "$S3_REGION"
    fi
    
    # Set up bucket policy for public read access
    echo -e "${YELLOW}🔒 Setting up bucket policy for public access...${NC}"
    cat > bucket-policy-temp.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${S3_BUCKET}/*"
        }
    ]
}
EOF
    
    aws s3api put-bucket-policy --bucket "${S3_BUCKET}" --policy file://bucket-policy-temp.json
    rm bucket-policy-temp.json
    
    echo -e "${GREEN}✅ S3 bucket created and configured${NC}"
else
    echo -e "${GREEN}✅ S3 bucket exists and accessible${NC}"
fi

# Check if we have changes to commit
if ! git diff --quiet HEAD -- "$NEWSLETTER_FILE" 2>/dev/null; then
    echo -e "${YELLOW}📝 Committing changes to Git...${NC}"
    git add "$NEWSLETTER_FILE"
    git commit -m "Update newsletter ${NEWSLETTER_FILE}: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}✅ Changes committed to Git${NC}"
else
    echo -e "${YELLOW}ℹ️  No changes detected in ${NEWSLETTER_FILE}${NC}"
fi

# Extract month name from filename for S3 key
MONTH_NAME=$(echo "$NEWSLETTER_FILE" | sed 's/_Enablement_Newsletter\.html//')
S3_KEY="${MONTH_NAME}_Enablement_Newsletter.html"

# Upload to S3
echo -e "${YELLOW}☁️  Uploading to S3...${NC}"
echo -e "${BLUE}   Source: ${NEWSLETTER_FILE}${NC}"
echo -e "${BLUE}   Target: s3://${S3_BUCKET}/${S3_KEY}${NC}"

aws s3 cp "$NEWSLETTER_FILE" "s3://${S3_BUCKET}/${S3_KEY}" \
    --content-type "text/html" \
    --cache-control "max-age=300" \
    --metadata "last-modified=$(date -u '+%Y-%m-%dT%H:%M:%SZ'),newsletter-month=${MONTH_NAME}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully deployed to S3!${NC}"
    echo -e "${GREEN}🌐 Newsletter available at: https://${S3_BUCKET}.s3.${S3_REGION}.amazonaws.com/${S3_KEY}${NC}"
else
    echo -e "${RED}❌ Failed to upload to S3${NC}"
    exit 1
fi

# Optional: Set up index.html redirect to latest newsletter
if [ "$NEWSLETTER_FILE" == "February_Enablement_Newsletter.html" ]; then
    echo -e "${YELLOW}🔗 Setting up index.html redirect to latest newsletter...${NC}"
    cat > index-temp.html << EOF
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=./${S3_KEY}">
    <title>Redirecting to Latest Newsletter...</title>
</head>
<body>
    <p>Redirecting to the latest newsletter...</p>
    <p>If you're not redirected, <a href="./${S3_KEY}">click here</a>.</p>
</body>
</html>
EOF
    aws s3 cp index-temp.html "s3://${S3_BUCKET}/index.html" --content-type "text/html"
    rm index-temp.html
    echo -e "${GREEN}✅ Index redirect created${NC}"
fi

# Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    echo -e "${YELLOW}⚠️  S3 deployment was successful, but Git push failed${NC}"
fi

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo -e "   📄 File: ${NEWSLETTER_FILE}"
echo -e "   🪣 Bucket: ${S3_BUCKET}"
echo -e "   🔗 URL: https://${S3_BUCKET}.s3.${S3_REGION}.amazonaws.com/${S3_KEY}"
echo -e "   📅 Deployed: $(date)"