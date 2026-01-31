# ComfyUI VOAI TTS 整合

這是一個將 VOAI TTS (語音合成) 整合到 ComfyUI 的擴展套件。

## 功能特色

- 🎙️ **短文本語音生成** - 適合簡短對話和提示音
- 📝 **長文本語音生成** - 支持複雜腳本和較長對話
- 👥 **多角色對話生成** - 支持複雜的對話場景
- 📋 **說話者列表查詢** - 取得可用的說話者
- 📊 **API 使用情況查詢** - 監控配額使用
- 🇹🇼 **繁體中文支援** - 原生支援繁體中文 TTS
- ⚙️ **豐富參數調整** - 語速、音調、風格權重等

## 安裝步驟

### 1. 下載或克隆此專案

將此專案放置在 ComfyUI 的 `custom_nodes` 目錄中：

``bash
cd ComfyUI/custom_nodes/
git clone <your-repo-url> ComfyUI-voai-NM
``

### 2. 安裝依賴

``bash
cd ComfyUI-voai-NM

# 安裝基礎依賴
pip install -r requirements.txt

# 安裝 VOAI SDK
cd voai-client-main
pip install -e .
cd ..
``

### 3. 設定 API Key

1. 複製 `.env.example` 為 `.env`
2. 在 `.env` 中設定您的 API key：

``
VOAI_API_KEY=你的API金鑰
``

3. 從 [VOAI 官網](https://voai.ai) 取得 API key

### 4. 重啟 ComfyUI

重新啟動 ComfyUI，載入新的節點。

## 可用節點

### 🎙️ VOAI Speech (短文本)

生成簡短的語音片段。

**輸入參數：**
- `text` - 要轉換的文本
- `speaker` - 說話者名稱（如：neo佑希）
- `version` - 模型版本（預設：Neo）
- `style` - 語音風格（預設：預設）
- `speed` - 語速 (0.5-2.0)
- `pitch_shift` - 音調偏移 (-12 到 12)
- `style_weight` - 風格權重 (0.0-1.0)
- `breath_pause` - 呼吸停頓 (0-10)
- `output_format` - wav 或 mp3
- `output_filename` - 輸出檔案名稱

**輸出：** AUDIO

### 🎙️ VOAI Voice (長文本)

生成較長的語音內容。

**輸入參數：**
- `voai_script_text` - VOAI 腳本文本（支持長文本）
- `speaker_name` - 說話者名稱
- 其他參數與 Speech 節點相同

**輸出：** AUDIO

### 👥 VOAI Dialogue (多角色)

生成多角色對話。

**輸入參數：**
- `dialogue_json` - 對話 JSON 格式
- `preset_speakers_json` - 預設說話者 JSON（選填）
- `output_format` - wav 或 mp3
- `output_filename` - 輸出檔案名稱

**對話 JSON 範例：**
``json
[
  {
    \"voai_script_text\": \"你好！\",
    \"preset_id\": \"neo佑希\"
  },
  {
    \"voai_script_text\": \"你好啊！\",
    \"preset_id\": \"neo夢夢\"
  }
]
``

**輸出：** AUDIO

### 📋 VOAI Get Speakers

查詢可用的說話者列表。

**輸出：** STRING (JSON 格式)

### 📊 VOAI Get Usage

查詢 API 使用配額。

**輸出：** STRING (JSON 格式)

## 使用範例

### 基本語音生成

1. 新增 **VOAI Speech** 節點
2. 輸入文本：「你好，歡迎使用 VOAI」
3. 選擇說話者：「neo佑希」
4. 連接到 **Save Audio** 節點
5. 執行工作流

### 長文本朗讀

1. 新增 **VOAI Voice** 節點
2. 輸入較長的文本內容
3. 選擇說話者
4. 調整語速和音調（可選）
5. 連接到 **Save Audio** 節點

### 多角色對話

1. 新增 **VOAI Dialogue** 節點
2. 在 `dialogue_json` 輸入對話 JSON
3. 連接到 **Save Audio** 節點
4. 生成完整對話音訊

## 常見說話者

- `neo佑希` - 女聲
- `neo夢夢` - 女聲
- `neo綾音` - 女聲
- `neo小天` - 男聲

*使用 VOAI Get Speakers 節點查看完整列表*

## 參數說明

### 語速 (speed)
- 範圍：0.5 - 2.0
- 預設：1.0
- 0.5 = 慢速，1.0 = 正常，2.0 = 快速

### 音調偏移 (pitch_shift)
- 範圍：-12 到 12
- 預設：0
- 負數降低音調，正數提高音調

### 風格權重 (style_weight)
- 範圍：0.0 - 1.0
- 預設：0.0
- 控制風格強度

### 呼吸停頓 (breath_pause)
- 範圍：0 - 10
- 預設：0
- 增加自然的呼吸停頓

## 故障排除

### 找不到 VOAI API key

確保：
1. `.env` 檔案在專案根目錄
2. 格式正確：`VOAI_API_KEY=你的key`
3. 已重啟 ComfyUI

### 音訊無法載入

確保已安裝：
``bash
pip install soundfile
``

### 模組導入錯誤

確保 VOAI SDK 已安裝：
``bash
cd voai-client-main
pip install -e .
``

## 測試範例

執行 `example_usage.py` 測試 API：

``bash
python example_usage.py
``

選項：
1. 短文本語音生成
2. 長文本語音生成
3. 多角色對話生成
4. 查詢說話者列表
5. 執行所有範例

## 更多資源

- [快速參考指南](QUICK_REFERENCE.md)
- [專案轉換摘要](CONVERSION_SUMMARY.md)
- [範例工作流](example_voai_workflow.json)
- [VOAI 官網](https://voai.ai)

## 授權

請參考 LICENSE 檔案。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯絡

有問題請開 Issue 或聯繫維護者。
