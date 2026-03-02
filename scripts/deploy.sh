#!/bin/bash
set -e

DEPLOY_DIR="/opt/realTimeMessageAlert"

rsync -av --exclude='__pycache__' --exclude='.git' --exclude='*.pyc' \
  ./ "$DEPLOY_DIR/"

echo "✅ 文件同步完成"
