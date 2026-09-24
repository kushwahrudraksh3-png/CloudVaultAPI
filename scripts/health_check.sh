#!/bin/bash

set -Eeuo pipefail

echo "================================="
echo "      CloudVault Health Check"
echo "================================="

echo ""
echo "Checking Django..."

python manage.py check


echo ""
echo "Checking PostgreSQL..."

pg_isready


echo ""
echo "Checking Redis..."

redis-cli ping


echo ""
echo "Checking Disk Space..."

df -h /
