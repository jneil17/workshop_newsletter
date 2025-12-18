#!/bin/bash

# Deploy script for January Enablement Newsletter
# This script uploads the HTML file to S3 and commits changes to Git

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📰 Deploying January Enablement Newsletter...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    exit 1
fi

# Check if the HTML file exists
if [ ! -f "January_Enablement_Newsletter.html" ]; then
    echo -e "${RED}❌ January_Enablement_Newsletter.html not found!${NC}"
    exit 1
fi

# Check if we have changes to commit
if ! git diff --quiet HEAD -- January_Enablement_Newsletter.html; then
    echo -e "${YELLOW}📝 Committing changes to Git...${NC}"
    git add January_Enablement_Newsletter.html
    git commit -m "Update newsletter: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}✅ Changes committed to Git${NC}"
else
    echo -e "${YELLOW}ℹ️  No changes detected in the HTML file${NC}"
fi

# Upload to S3
echo -e "${YELLOW}☁️  Uploading to S3...${NC}"
aws s3 cp January_Enablement_Newsletter.html s3://databricks-january-workshops/January_Enablement_Newsletter.html \
    --content-type "text/html" \
    --cache-control "max-age=300" \
    --metadata "last-modified=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully deployed to S3!${NC}"
    echo -e "${GREEN}🌐 Newsletter available at: https://databricks-january-workshops.s3.us-east-1.amazonaws.com/January_Enablement_Newsletter.html${NC}"
else
    echo -e "${RED}❌ Failed to upload to S3${NC}"
    exit 1
fi

# Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Deployment complete!${NC}"