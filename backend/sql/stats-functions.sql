-- ========================================
-- 9. 最弱詞語排名 (錯誤率最高)
-- ========================================
CREATE OR REPLACE FUNCTION get_weakest_words(
    p_limit INTEGER DEFAULT 10,
    p_min_attempts INTEGER DEFAULT 3
)
RETURNS TABLE (
    id INTEGER,
    chinese TEXT,
    english TEXT,
    category VARCHAR,
    total_attempts INTEGER,
    correct_count INTEGER,
    accuracy_percent NUMERIC,
    avg_time_ms NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w.id,
        w.chinese,
        w.english,
        w.category,
        COUNT(lr.id)::INTEGER AS total_attempts,
        SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END)::INTEGER AS correct_count,
        ROUND(
            100.0 * SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) / COUNT(lr.id),
            2
        ) AS accuracy_percent,
        AVG(lr.time_spent_ms) AS avg_time_ms
    FROM words w
    JOIN learning_records lr ON w.id = lr.word_id
    GROUP BY w.id, w.chinese, w.english, w.category
    HAVING COUNT(lr.id) >= p_min_attempts
    ORDER BY accuracy_percent ASC, total_attempts DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_weakest_words TO web_anon;


-- ========================================
-- 10. 學習時間統計 (按日期)
-- ========================================
CREATE OR REPLACE FUNCTION get_learning_time_stats(
    p_days INTEGER DEFAULT 7
)
RETURNS TABLE (
    date DATE,
    total_attempts INTEGER,
    correct_count INTEGER,
    accuracy_percent NUMERIC,
    total_time_minutes NUMERIC,
    avg_time_per_word_ms NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(lr.created_at) AS date,
        COUNT(*)::INTEGER AS total_attempts,
        SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END)::INTEGER AS correct_count,
        ROUND(
            100.0 * SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) / COUNT(*),
            2
        ) AS accuracy_percent,
        ROUND(SUM(lr.time_spent_ms) / 60000.0, 2) AS total_time_minutes,
        AVG(lr.time_spent_ms) AS avg_time_per_word_ms
    FROM learning_records lr
    WHERE lr.created_at >= CURRENT_DATE - INTERVAL '1 day' * p_days
    GROUP BY DATE(lr.created_at)
    ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_learning_time_stats TO web_anon;


-- ========================================
-- 11. 遊戲模式統計
-- ========================================
CREATE OR REPLACE FUNCTION get_game_mode_stats()
RETURNS TABLE (
    game_type VARCHAR,
    total_attempts INTEGER,
    correct_count INTEGER,
    accuracy_percent NUMERIC,
    avg_time_ms NUMERIC,
    last_played_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lr.game_type,
        COUNT(*)::INTEGER AS total_attempts,
        SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END)::INTEGER AS correct_count,
        ROUND(
            100.0 * SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) / COUNT(*),
            2
        ) AS accuracy_percent,
        AVG(lr.time_spent_ms) AS avg_time_ms,
        MAX(lr.created_at) AS last_played_at
    FROM learning_records lr
    GROUP BY lr.game_type
    ORDER BY total_attempts DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_game_mode_stats TO web_anon;


-- ========================================
-- 12. 詞語分類統計
-- ========================================
CREATE OR REPLACE FUNCTION get_category_stats()
RETURNS TABLE (
    category VARCHAR,
    total_words INTEGER,
    practiced_words INTEGER,
    mastered_words INTEGER,
    avg_accuracy NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w.category,
        COUNT(DISTINCT w.id)::INTEGER AS total_words,
        COUNT(DISTINCT CASE WHEN lr.id IS NOT NULL THEN w.id END)::INTEGER AS practiced_words,
        COUNT(DISTINCT CASE 
            WHEN stats.accuracy_percent >= 80 AND stats.total_attempts >= 3 
            THEN w.id 
        END)::INTEGER AS mastered_words,
        COALESCE(AVG(stats.accuracy_percent), 0) AS avg_accuracy
    FROM words w
    LEFT JOIN learning_records lr ON w.id = lr.word_id
    LEFT JOIN (
        SELECT 
            word_id,
            ROUND(
                100.0 * SUM(CASE WHEN correct THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) AS accuracy_percent,
            COUNT(*) AS total_attempts
        FROM learning_records
        GROUP BY word_id
    ) stats ON w.id = stats.word_id
    GROUP BY w.category
    ORDER BY total_words DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_category_stats TO web_anon;


-- ========================================
-- 13. 成就進度統計
-- ========================================
CREATE OR REPLACE FUNCTION get_achievement_progress()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_words_practiced', (
            SELECT COUNT(DISTINCT word_id) FROM learning_records
        ),
        'total_attempts', (
            SELECT COUNT(*) FROM learning_records
        ),
        'total_correct', (
            SELECT COUNT(*) FROM learning_records WHERE correct = true
        ),
        'overall_accuracy', (
            SELECT ROUND(
                100.0 * COUNT(CASE WHEN correct THEN 1 END) / COUNT(*),
                2
            )
            FROM learning_records
        ),
        'total_time_hours', (
            SELECT ROUND(SUM(time_spent_ms) / 3600000.0, 2)
            FROM learning_records
        ),
        'streak_days', (
            -- Calculate consecutive days with practice
            WITH daily_practice AS (
                SELECT DISTINCT DATE(created_at) AS practice_date
                FROM learning_records
                ORDER BY practice_date DESC
            ),
            streak AS (
                SELECT 
                    COUNT(*) AS days
                FROM daily_practice
                WHERE practice_date >= CURRENT_DATE - INTERVAL '1 day' * (
                    SELECT COUNT(*) FROM daily_practice
                )
            )
            SELECT COALESCE(MAX(days), 0) FROM streak
        ),
        'mastered_words', (
            -- Words with >=80% accuracy and >=3 attempts
            SELECT COUNT(DISTINCT word_id)
            FROM (
                SELECT 
                    word_id,
                    COUNT(*) AS attempts,
                    SUM(CASE WHEN correct THEN 1 ELSE 0 END) AS correct_count
                FROM learning_records
                GROUP BY word_id
            ) stats
            WHERE attempts >= 3 
            AND (100.0 * correct_count / attempts) >= 80
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_achievement_progress TO web_anon;


-- ========================================
-- 14. 最近學習記錄 (用於 dashboard)
-- ========================================
CREATE OR REPLACE FUNCTION get_recent_learning_activity(
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    word_id INTEGER,
    chinese TEXT,
    english TEXT,
    game_type VARCHAR,
    correct BOOLEAN,
    time_spent_ms INTEGER,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lr.id,
        lr.word_id,
        w.chinese,
        w.english,
        lr.game_type,
        lr.correct,
        lr.time_spent_ms,
        lr.created_at
    FROM learning_records lr
    JOIN words w ON lr.word_id = w.id
    ORDER BY lr.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_recent_learning_activity TO web_anon;
