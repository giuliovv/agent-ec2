#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./deploy_frontend.sh <bucket-name> <region>
# Example:
#   ./deploy_frontend.sh agent-ec2-frontend us-east-1

BUCKET=${1:?bucket name required}
REGION=${2:-us-east-1}
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"

aws s3 mb "s3://$BUCKET" --region "$REGION" || true
aws s3 sync "$FRONTEND_DIR" "s3://$BUCKET" --delete --region "$REGION"

echo "Frontend synced to s3://$BUCKET"
echo "Next: create CloudFront distribution with this bucket as origin."
