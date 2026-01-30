#!/bin/bash
# SpellQuest - Apply functions.sql to existing database
# 適用於已經 running 嘅 PostgreSQL container

set -e

echo "🔧 Applying functions.sql to existing database..."

# Check if container is running
if ! docker ps | grep -q spellquest_db; then
    echo "❌ Error: spellquest_db container is not running"
    echo "Please start it first: docker-compose up -d postgres"
    exit 1
fi

# Apply functions.sql
docker exec -i spellquest_db psql -U postgres -d spellquest < backend/sql/functions.sql

echo "✅ Functions applied successfully!"
echo ""
echo "📝 You can verify by running:"
echo "   docker exec -it spellquest_db psql -U postgres -d spellquest -c '\\df'"
echo ""
echo "🧪 Test a function:"
echo "   docker exec -it spellquest_db psql -U postgres -d spellquest -c \"SELECT * FROM get_random_words('fruit', 'P1', 5);\""
