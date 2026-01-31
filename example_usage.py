"""
Simple example of using VOAI TTS API directly
This demonstrates the basic API usage without ComfyUI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加入 VOAI SDK 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voai-client-main', 'src'))
from voai_client import VoiceAPI, APIError

# Load environment variables from .env file
load_dotenv()


def example_speech():
    """
    範例 1: 生成短文本語音 (Speech)
    """
    print("=" * 60)
    print("🎙️ VOAI Speech 範例 (短文本)")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('VOAI_API_KEY')
    if not api_key:
        print("❌ Error: VOAI_API_KEY not found")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your VOAI API key")
        print("3. Get key from: https://voai.ai")
        return
    
    try:
        # 初始化 VOAI client
        client = VoiceAPI(api_key=api_key)
        print("✅ API Key loaded")
        print()
        
        # 生成語音
        text = "你好！歡迎使用 VOAI 語音合成服務。"
        speaker = "neo佑希"
        
        print(f"📝 文本: {text}")
        print(f"🎭 說話者: {speaker}")
        print("🚀 生成語音中...")
        print()
        
        audio_bytes = client.speech(
            text=text,
            speaker=speaker,
            version="Neo",
            style="預設",
            speed=1.0,
            output_format="wav"
        )
        
        # 儲存音訊
        output_filename = "voai_speech_example.wav"
        with open(output_filename, 'wb') as f:
            f.write(audio_bytes)
        
        print(f"✅ 語音生成成功！")
        print(f"📁 已儲存至: {output_filename}")
        print()
        
    except APIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_voice():
    """
    範例 2: 生成長文本語音 (Voice)
    """
    print("=" * 60)
    print("🎙️ VOAI Voice 範例 (長文本)")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('VOAI_API_KEY')
    if not api_key:
        print("❌ Error: VOAI_API_KEY not found")
        return
    
    try:
        # 初始化 VOAI client
        client = VoiceAPI(api_key=api_key)
        print("✅ API Key loaded")
        print()
        
        # 生成語音
        script_text = """
        這是一個較長的文本範例。
        
        VOAI 語音合成系統可以處理多行文本，
        並且支援繁體中文的自然語音生成。
        
        您可以調整語速、音調、風格等參數，
        來獲得最適合您需求的語音效果。
        """
        
        speaker = "neo夢夢"
        
        print(f"📝 文本長度: {len(script_text)} 字元")
        print(f"🎭 說話者: {speaker}")
        print("🚀 生成語音中...")
        print()
        
        audio_bytes = client.generate_voice(
            voai_script_text=script_text,
            name=speaker,
            model="Neo",
            style="預設",
            speed=1.0,
            output_format="wav"
        )
        
        # 儲存音訊
        output_filename = "voai_voice_example.wav"
        with open(output_filename, 'wb') as f:
            f.write(audio_bytes)
        
        print(f"✅ 語音生成成功！")
        print(f"📁 已儲存至: {output_filename}")
        print()
        
    except APIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_dialogue():
    """
    範例 3: 生成多角色對話 (Dialogue)
    """
    print("=" * 60)
    print("👥 VOAI Dialogue 範例 (多角色對話)")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('VOAI_API_KEY')
    if not api_key:
        print("❌ Error: VOAI_API_KEY not found")
        return
    
    try:
        # 初始化 VOAI client
        client = VoiceAPI(api_key=api_key)
        print("✅ API Key loaded")
        print()
        
        # 對話內容
        dialogue = [
            {
                "voai_script_text": "你好！今天天氣真好。",
                "preset_id": "neo佑希"
            },
            {
                "voai_script_text": "是啊，要不要一起去散步？",
                "preset_id": "neo夢夢"
            },
            {
                "voai_script_text": "好啊！我們走吧。",
                "preset_id": "neo佑希"
            }
        ]
        
        print(f"👥 對話段落數: {len(dialogue)}")
        print("🚀 生成對話中...")
        print()
        
        audio_bytes = client.generate_dialogue(
            dialogue=dialogue,
            output_format="wav"
        )
        
        # 儲存音訊
        output_filename = "voai_dialogue_example.wav"
        with open(output_filename, 'wb') as f:
            f.write(audio_bytes)
        
        print(f"✅ 對話生成成功！")
        print(f"📁 已儲存至: {output_filename}")
        print()
        
    except APIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_speakers():
    """
    範例 4: 查詢可用的說話者
    """
    print("=" * 60)
    print("📋 查詢 VOAI 說話者列表")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('VOAI_API_KEY')
    if not api_key:
        print("❌ Error: VOAI_API_KEY not found")
        return
    
    try:
        # 初始化 VOAI client
        client = VoiceAPI(api_key=api_key)
        print("✅ API Key loaded")
        print()
        
        # 取得說話者列表
        print("🔍 查詢說話者中...")
        speakers = client.get_speakers()
        
        print(f"✅ 找到 {len(speakers)} 位說話者：")
        print()
        
        import json
        print(json.dumps(speakers, ensure_ascii=False, indent=2))
        print()
        
    except APIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """
    主程式：執行所有範例
    """
    print("\n")
    print("=" * 70)
    print("🎙️ VOAI TTS API 使用範例")
    print("=" * 70)
    print()
    print("請選擇要執行的範例：")
    print("1. 短文本語音生成 (Speech)")
    print("2. 長文本語音生成 (Voice)")
    print("3. 多角色對話生成 (Dialogue)")
    print("4. 查詢說話者列表")
    print("5. 執行所有範例")
    print("0. 離開")
    print()
    
    choice = input("請輸入選項 (0-5): ").strip()
    print()
    
    if choice == "1":
        example_speech()
    elif choice == "2":
        example_voice()
    elif choice == "3":
        example_dialogue()
    elif choice == "4":
        get_speakers()
    elif choice == "5":
        example_speech()
        print()
        example_voice()
        print()
        example_dialogue()
        print()
        get_speakers()
    elif choice == "0":
        print("👋 再見！")
        return
    else:
        print("❌ 無效的選項")
        return
    
    print()
    print("=" * 70)
    print("🎉 執行完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()

        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Please check:")
        print("1. Your API token is valid")
        print("2. You have sufficient credits")
        print("3. The URLs are accessible")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
