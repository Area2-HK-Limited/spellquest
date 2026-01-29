-- SpellQuest Custom PostgreSQL Functions
-- 用於遊戲邏輯和數據查詢

-- ========================================
-- 1. 隨機抽詞語 (用於遊戲)
-- ========================================
CREATE OR REPLACE FUNCTION get_random_words(
    p_category VARCHAR DEFAULT NULL,
    p_grade VARCHAR DEFAULT 'P1',
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    chinese TEXT,
    english TEXT,
    pinyin TEXT,
    category VARCHAR,
    grade VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w.id,
        w.chinese,
        w.english,
        w.pinyin,
        w.category,
        w.grade
    FROM words w
    WHERE 
        (p_category IS NULL OR w.category = p_category)
        AND w.grade = p_grade
    ORDER BY RANDOM()
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- 授權
GRANT EXECUTE ON FUNCTION get_random_words TO web_anon;


-- ========================================
-- 2. 根據詞語集生成題目
-- ========================================
CREATE OR REPLACE FUNCTION get_quiz_questions(
    p_word_set_id INTEGER
)
RETURNS TABLE (
    id INTEGER,
    chinese TEXT,
    english TEXT,
    pinyin TEXT,
    category VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w.id,
        w.chinese,
        w.english,
        w.pinyin,
        w.category
    FROM words w
    JOIN word_set_items wsi ON w.id = wsi.word_id
    WHERE wsi.word_set_id = p_word_set_id
    ORDER BY wsi.order_num;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_quiz_questions TO web_anon;


-- ========================================
-- 3. 提交學習記錄 (with validation)
-- ========================================
CREATE OR REPLACE FUNCTION submit_learning_record(
    p_word_id INTEGER,
    p_game_type VARCHAR,
    p_correct BOOLEAN,
    p_time_spent_ms INTEGER
)
RETURNS INTEGER AS $$
DECLARE
    v_record_id INTEGER;
BEGIN
    -- Validate word exists
    IF NOT EXISTS (SELECT 1 FROM words WHERE id = p_word_id) THEN
        RAISE EXCEPTION 'Word ID % does not exist', p_word_id;
    END IF;

    -- Validate game type
    IF p_game_type NOT IN ('spelling', 'sentence', 'flashcard') THEN
        RAISE EXCEPTION 'Invalid game type: %', p_game_type;
    END IF;

    -- Insert record
    INSERT INTO learning_records (word_id, game_type, correct, time_spent_ms)
    VALUES (p_word_id, p_game_type, p_correct, p_time_spent_ms)
    RETURNING id INTO v_record_id;

    RETURN v_record_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION submit_learning_record TO web_anon;


-- ========================================
-- 4. 獲取隨機句子
-- ========================================
CREATE OR REPLACE FUNCTION get_random_sentences(
    p_category VARCHAR DEFAULT NULL,
    p_grade VARCHAR DEFAULT 'P1',
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id INTEGER,
    content TEXT,
    translation TEXT,
    category VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.content,
        s.translation,
        s.category
    FROM sentences s
    WHERE 
        (p_category IS NULL OR s.category = p_category)
        AND s.grade = p_grade
    ORDER BY RANDOM()
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_random_sentences TO web_anon;


-- ========================================
-- 5. 詞語準確率統計 (View)
-- ========================================
CREATE OR REPLACE VIEW word_accuracy_stats AS
SELECT 
    w.id,
    w.chinese,
    w.english,
    w.category,
    COUNT(lr.id) AS total_attempts,
    SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) AS correct_count,
    ROUND(
        100.0 * SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) / NULLIF(COUNT(lr.id), 0),
        2
    ) AS accuracy_percent,
    AVG(lr.time_spent_ms) AS avg_time_ms
FROM words w
LEFT JOIN learning_records lr ON w.id = lr.word_id
GROUP BY w.id, w.chinese, w.english, w.category;

GRANT SELECT ON word_accuracy_stats TO web_anon;


-- ========================================
-- 6. 學習進度統計 (View)
-- ========================================
CREATE OR REPLACE VIEW learning_progress AS
SELECT 
    lr.game_type,
    DATE(lr.created_at) AS date,
    COUNT(*) AS total_attempts,
    SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) AS correct_count,
    ROUND(
        100.0 * SUM(CASE WHEN lr.correct THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS accuracy_percent
FROM learning_records lr
GROUP BY lr.game_type, DATE(lr.created_at)
ORDER BY DATE(lr.created_at) DESC, lr.game_type;

GRANT SELECT ON learning_progress TO web_anon;


-- ========================================
-- 7. 獲取詞語集詳情 (with words)
-- ========================================
CREATE OR REPLACE FUNCTION get_word_set_details(
    p_word_set_id INTEGER
)
RETURNS TABLE (
    word_set_id INTEGER,
    word_set_name VARCHAR,
    word_set_description TEXT,
    word_id INTEGER,
    chinese TEXT,
    english TEXT,
    pinyin TEXT,
    order_num INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ws.id AS word_set_id,
        ws.name AS word_set_name,
        ws.description AS word_set_description,
        w.id AS word_id,
        w.chinese,
        w.english,
        w.pinyin,
        wsi.order_num
    FROM word_sets ws
    JOIN word_set_items wsi ON ws.id = wsi.word_set_id
    JOIN words w ON wsi.word_id = w.id
    WHERE ws.id = p_word_set_id
    ORDER BY wsi.order_num;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION get_word_set_details TO web_anon;


-- ========================================
-- 8. 批量插入詞語 (for OCR import)
-- ========================================
CREATE OR REPLACE FUNCTION bulk_insert_words(
    p_words JSONB
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_word JSONB;
BEGIN
    FOR v_word IN SELECT * FROM jsonb_array_elements(p_words)
    LOOP
        INSERT INTO words (chinese, english, pinyin, category, grade)
        VALUES (
            v_word->>'chinese',
            v_word->>'english',
            v_word->>'pinyin',
            COALESCE(v_word->>'category', 'general'),
            COALESCE(v_word->>'grade', 'P1')
        );
        v_count := v_count + 1;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

GRANT EXECUTE ON FUNCTION bulk_insert_words TO web_anon;


-- ========================================
-- 測試查詢
-- ========================================

-- 測試隨機抽詞
-- SELECT * FROM get_random_words('fruit', 'P1', 5);

-- 測試題目生成
-- SELECT * FROM get_quiz_questions(1);

-- 測試提交記錄
-- SELECT submit_learning_record(1, 'spelling', true, 5000);

-- 測試準確率
-- SELECT * FROM word_accuracy_stats WHERE total_attempts > 0;

-- 測試學習進度
-- SELECT * FROM learning_progress;

-- 完成提示
DO $$
BEGIN
    RAISE NOTICE 'SpellQuest custom functions created!';
    RAISE NOTICE 'Functions: get_random_words, get_quiz_questions, submit_learning_record, get_random_sentences, get_word_set_details, bulk_insert_words';
    RAISE NOTICE 'Views: word_accuracy_stats, learning_progress';
END $$;
