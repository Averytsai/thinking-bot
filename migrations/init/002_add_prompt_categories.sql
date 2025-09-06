-- 思考機器人資料庫擴展腳本
-- 新增問題分類表和會話狀態欄位

-- 建立問題分類表
CREATE TABLE prompt_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    example TEXT,
    prompt_template TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 為會話表新增欄位
ALTER TABLE conversations ADD COLUMN category_key VARCHAR(100);
ALTER TABLE conversations ADD COLUMN state VARCHAR(50) DEFAULT 'initial';
ALTER TABLE conversations ADD COLUMN selected_category_id UUID REFERENCES prompt_categories(id);

-- 建立索引
CREATE INDEX idx_prompt_categories_key ON prompt_categories(category_key);
CREATE INDEX idx_prompt_categories_active ON prompt_categories(is_active);
CREATE INDEX idx_conversations_state ON conversations(state);
CREATE INDEX idx_conversations_category ON conversations(category_key);

-- 為prompt_categories表建立觸發器
CREATE TRIGGER update_prompt_categories_updated_at BEFORE UPDATE ON prompt_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入5個問題分類
INSERT INTO prompt_categories (category_key, name, description, example, prompt_template) VALUES 
('task_thinking', '收到任務的時候，該如何思考任務', '協助你分析任務需求，制定執行計劃', '例如：如何拆解複雜專案、如何評估任務難度、如何制定時間規劃', '你是一個任務分析專家，擅長幫助用戶深入思考任務的本質和執行方法。請協助用戶分析任務需求，提供結構化的思考框架和實用的執行建議。'),

('team_discussion', '遇到問題的時候，該怎麼跟團隊討論', '協助你準備團隊討論，有效溝通問題', '例如：如何準備討論議題、如何引導團隊思考、如何達成共識', '你是一個團隊協作專家，擅長幫助用戶準備和進行有效的團隊討論。請協助用戶整理問題、準備討論材料，並提供溝通技巧和討論引導方法。'),

('work_reporting', '報告工作結果的時候順序該如何排', '協助你組織工作報告，突出重點成果', '例如：如何組織報告結構、如何突出關鍵成果、如何處理問題和挑戰', '你是一個工作報告專家，擅長幫助用戶組織和呈現工作成果。請協助用戶整理報告結構，突出重點成果，並提供清晰有效的報告呈現方法。'),

('viewpoint_sharing', '我該如何有效的分享我的觀點？', '協助你表達觀點，影響他人理解', '例如：如何組織論點、如何提供證據支持、如何處理反對意見', '你是一個觀點表達專家，擅長幫助用戶有效地分享和說服他人接受自己的觀點。請協助用戶組織論點、準備支持材料，並提供說服技巧和溝通策略。'),

('meeting_summary', '我該如何做會議或是專案總結', '協助你總結會議和專案，提取關鍵要點', '例如：如何整理會議記錄、如何提取關鍵決策、如何制定後續行動', '你是一個會議和專案總結專家，擅長幫助用戶整理和總結重要信息。請協助用戶提取關鍵要點，組織總結結構，並提供後續行動建議。');

-- 顯示建立完成的訊息
DO $$
BEGIN
    RAISE NOTICE '資料庫擴展完成！';
    RAISE NOTICE '已建立表: prompt_categories';
    RAISE NOTICE '已擴展表: conversations (新增 category_key, state, selected_category_id)';
    RAISE NOTICE '已插入5個問題分類';
END $$;
