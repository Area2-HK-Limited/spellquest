#!/bin/bash
# SpellQuest - Apply functions to existing database
# 適用於已經 running 嘅 PostgreSQL container

set -e

echo "🔧 Applying SQL functions to existing database..."

# Check if container is running
if ! docker ps | grep -q spellquest_db; then
    echo "❌ Error: spellquest_db container is not running"
    echo "Please start it first: docker-compose up -d postgres"
    exit 1
fi

# Apply functions.sql
echo "📝 Applying functions.sql..."
docker exec -i spellquest_db psql -U postgres -d spellquest < backend/sql/functions.sql

# Apply stats-functions.sql
echo "📊 Applying stats-functions.sql..."
docker exec -i spellquest_db psql -U postgres -d spellquest < backend/sql/stats-functions.sql

echo ""
echo "✅ All functions applied successfully!"
echo ""
echo "📝 You can verify by running:"
echo "   docker exec -it spellquest_db psql -U postgres -d spellquest -c '\\df'"
echo ""
echo "🧪 Test functions:"
echo "   # Get weakest words"
echo "   docker exec -it spellquest_db psql -U postgres -d spellquest -c \"SELECT * FROM get_weakest_words(5);\""
echo ""
echo "   # Get achievement progress"
echo "   docker exec -it spellquest_db psql -U postgres -d spellquest -c \"SELECT get_achievement_progress();\""
