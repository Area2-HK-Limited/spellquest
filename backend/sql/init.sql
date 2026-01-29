-- SpellQuest Database Schema
-- 初始化腳本

-- 創建角色
CREATE ROLE web_anon NOLOGIN;

-- 詞語表
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    chinese TEXT NOT NULL,
    english TEXT,
    pinyin TEXT,
    category VARCHAR(50) DEFAULT 'general',
    grade VARCHAR(10) DEFAULT 'P1',
    audio_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 句子表
CREATE TABLE IF NOT EXISTS sentences (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    translation TEXT,
    category VARCHAR(50) DEFAULT 'general',
    grade VARCHAR(10) DEFAULT 'P1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 詞語集（用於分組溫習）
CREATE TABLE IF NOT EXISTS word_sets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    grade VARCHAR(10) DEFAULT 'P1',
    subject VARCHAR(20) DEFAULT 'chinese',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 詞語集關聯
CREATE TABLE IF NOT EXISTS word_set_items (
    id SERIAL PRIMARY KEY,
    word_set_id INTEGER REFERENCES word_sets(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    order_num INTEGER DEFAULT 0
);

-- 學習記錄
CREATE TABLE IF NOT EXISTS learning_records (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id),
    game_type VARCHAR(20),
    correct BOOLEAN,
    time_spent_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引
CREATE INDEX IF NOT EXISTS idx_words_category ON words(category);
CREATE INDEX IF NOT EXISTS idx_words_grade ON words(grade);
CREATE INDEX IF NOT EXISTS idx_sentences_category ON sentences(category);
CREATE INDEX IF NOT EXISTS idx_learning_records_word_id ON learning_records(word_id);

-- 插入示例數據：中文詞語
INSERT INTO words (chinese, english, pinyin, category, grade) VALUES
('蘋果', 'apple', 'píng guǒ', 'fruit', 'P1'),
('香蕉', 'banana', 'xiāng jiāo', 'fruit', 'P1'),
('橙', 'orange', 'chéng', 'fruit', 'P1'),
('書包', 'school bag', 'shū bāo', 'school', 'P1'),
('鉛筆', 'pencil', 'qiān bǐ', 'school', 'P1'),
('老師', 'teacher', 'lǎo shī', 'school', 'P1'),
('學生', 'student', 'xué shēng', 'school', 'P1'),
('爸爸', 'father', 'bà ba', 'family', 'P1'),
('媽媽', 'mother', 'mā ma', 'family', 'P1'),
('哥哥', 'elder brother', 'gē ge', 'family', 'P1'),
('姐姐', 'elder sister', 'jiě jie', 'family', 'P1'),
('弟弟', 'younger brother', 'dì di', 'family', 'P1'),
('妹妹', 'younger sister', 'mèi mei', 'family', 'P1'),
('太陽', 'sun', 'tài yáng', 'nature', 'P1'),
('月亮', 'moon', 'yuè liang', 'nature', 'P1'),
('星星', 'star', 'xīng xīng', 'nature', 'P1');

-- 插入示例句子
INSERT INTO sentences (content, translation, category, grade) VALUES
('I have a red apple.', '我有一個紅蘋果。', 'fruit', 'P1'),
('The cat is sleeping.', '貓正在睡覺。', 'animals', 'P1'),
('I go to school.', '我去上學。', 'school', 'P1'),
('This is my book.', '這是我的書。', 'school', 'P1'),
('I love my family.', '我愛我的家人。', 'family', 'P1');

-- 創建示例詞語集
INSERT INTO word_sets (name, description, grade, subject) VALUES
('第22週中文默書', '1月28日默書範圍', 'P1', 'chinese'),
('水果詞語', '常見水果名稱', 'P1', 'chinese'),
('學校用品', '學校常用物品', 'P1', 'chinese');

-- 設置權限
GRANT USAGE ON SCHEMA public TO web_anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO web_anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO web_anon;

-- 更新時間觸發器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_words_updated_at 
    BEFORE UPDATE ON words
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 完成提示
DO $$
BEGIN
    RAISE NOTICE 'SpellQuest database initialized!';
    RAISE NOTICE 'Words: %', (SELECT COUNT(*) FROM words);
    RAISE NOTICE 'Sentences: %', (SELECT COUNT(*) FROM sentences);
END $$;
