"""
ComfyUI VOAI API 整合模組
支援 VOAI TTS 語音生成服務
"""

import os
import json
from .voai_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 註冊自訂 API 路由
try:
    from aiohttp import web
    from server import PromptServer

    @PromptServer.instance.routes.get("/voai/speakers")
    async def get_voai_speakers(request):
        """GET /voai/speakers - 取得所有模型支援的配音員"""
        try:
            from .voai_api import VoaiAPI
            api = VoaiAPI()
            speakers = api.get_speakers()
            return web.json_response({"success": True, "data": speakers})
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=500)

    print("✅ 已註冊 API 路由: GET /voai/speakers")
except Exception as e:
    print(f"⚠️ 無法註冊 API 路由（可能不在 ComfyUI 環境中）: {e}")

# 載入 API key
def load_api_key():
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('!'):
                        continue
                    if 'VOAI_API_KEY' in line:
                        if '=' in line:
                            key = line.split('=', 1)[1].strip().strip('"\'')
                            if key and key != '<paste-your-key-here>':
                                os.environ['VOAI_API_KEY'] = key
                                print("✅ 已從 .env 檔案載入 VOAI API key")
                                return
            print("⚠️ VOAI_API_KEY 未在 .env 檔案中配置")
            print("   請編輯 .env 並設定: VOAI_API_KEY=<your-key>")
        else:
            print("⚠️ 找不到 .env 檔案。請建立一個並設定 VOAI_API_KEY")
            print("   從 VOAI 官網取得 API key: https://voai.ai")
    except Exception as e:
        print(f"❌ 載入 API key 時發生錯誤: {e}")

# 模組載入時載入 API key
load_api_key()

# 顯示歡迎訊息
print("=" * 70)
print("🎙️ ComfyUI VOAI TTS - 語音生成支援 v1.0")
print("=" * 70)
print("📦 支援的功能：")
print("   🎙️ 短文本語音生成 (Speech)")
print("   📝 長文本語音生成 (Voice)")
print("   👥 多角色對話生成 (Dialogue)")
print("   📋 說話者列表查詢")
print("   📊 API 使用情況查詢")
print("=" * 70)
print("✨ 特色：")
print("   🇹🇼 支援繁體中文 TTS")
print("   🎭 多種說話者與風格")
print("   ⚙️ 可調整語速、音調、風格權重")
print("   🔄 影片+音訊合併 - 無縫結合影片與音訊")
print("=" * 70)
print("🔑 API Tokens: https://replicate.com/account/api-tokens")
print("📚 文件: https://replicate.com/")
print("=" * 70)

# ComfyUI 相容性
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
