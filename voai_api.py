"""
VOAI API 整合模組 for ComfyUI
支援 VOAI TTS 語音生成服務
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# 嘗試載入 VOAI SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voai-client-main', 'src'))
from voai_client import VoiceAPI, APIError

# Load environment variables
load_dotenv()

# Also try to load from the plugin directory
plugin_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(plugin_dir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Try to import ComfyUI's folder_paths, use fallback if not available
try:
    import folder_paths
except ImportError:
    # Fallback for testing outside ComfyUI environment
    class FolderPaths:
        @staticmethod
        def get_output_directory():
            return os.path.join(os.getcwd(), "output")
    folder_paths = FolderPaths()


def get_unique_filename(output_dir: str, base_name: str, extension: str) -> str:
    """
    生成唯一的檔案名稱，使用8位序號
    
    Args:
        output_dir: 輸出目錄
        base_name: 基礎檔名
        extension: 副檔名（不含點）
    
    Returns:
        完整的檔案路徑
    """
    counter = 1
    while True:
        filename = f"{base_name}_{counter:08d}.{extension}"
        full_path = os.path.join(output_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        counter += 1
        if counter > 99999999:  # 防止無限迴圈
            import time
            filename = f"{base_name}_{int(time.time())}.{extension}"
            return os.path.join(output_dir, filename)


class VoaiAPI:
    """
    VOAI TTS API 客戶端，支援語音生成
    """
    
    def __init__(self, api_key=None):
        """
        初始化 VOAI API 客戶端
        
        Args:
            api_key (str, optional): VOAI API key. 若未提供，將從環境變數讀取。
        """
        self.api_key = api_key or os.getenv('VOAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "找不到 VOAI API key。請執行以下任一方式：\n"
                "1. 在 .env 檔案中設定 VOAI_API_KEY\n"
                "2. 初始化 VoaiAPI 時提供 api_key 參數\n"
                "從 VOAI 官網取得 API key: https://voai.ai"
            )
        
        # 初始化 VOAI client
        self.client = VoiceAPI(api_key=self.api_key)
        
        print("✅ VOAI API 初始化成功")
    
    def get_speakers(self) -> List[Dict[str, Any]]:
        """
        取得可用的說話者列表
        
        Returns:
            List[Dict]: 說話者列表，每個說話者包含 name, styles, age, gender 等資訊
        """
        try:
            print("📋 取得說話者列表...")
            response = self.client.get_speakers()
            
            # 解析 API 回應結構: {"data": {"models": [{"info": {...}, "speakers": [...]}]}}
            if isinstance(response, dict) and 'data' in response:
                data = response['data']
                if isinstance(data, dict) and 'models' in data:
                    models = data['models']
                    if isinstance(models, list):
                        # 收集所有模型的說話者
                        all_speakers = []
                        for model in models:
                            if isinstance(model, dict) and 'speakers' in model:
                                speakers = model.get('speakers', [])
                                all_speakers.extend(speakers)
                        
                        if all_speakers:
                            print(f"✅ 找到 {len(all_speakers)} 位說話者")
                            return all_speakers
            
            print("⚠️ 未找到說話者列表")
            return []
        except APIError as e:
            print(f"❌ 取得說話者列表時發生錯誤: {e}")
            return []
    
    def generate_speech(
        self,
        text: str,
        speaker: str,
        version: str = "Neo",
        style: str = "預設",
        speed: float = 1.0,
        pitch_shift: int = 0,
        style_weight: float = 0.0,
        breath_pause: int = 0,
        output_format: str = "wav",
        output_filename: str = "voai_speech"
    ) -> Optional[str]:
        """
        生成短文本語音 (使用 /TTS/Speech endpoint)
        
        Args:
            text (str): 要轉換的文本
            speaker (str): 說話者名稱
            version (str): 模型版本，預設 "Neo"
            style (str): 語音風格，預設 "預設"
            speed (float): 語速，預設 1.0
            pitch_shift (int): 音調偏移，預設 0
            style_weight (float): 風格權重，預設 0.0
            breath_pause (int): 呼吸停頓，預設 0
            output_format (str): 輸出格式，預設 "wav"
            output_filename (str): 輸出檔案名稱
        
        Returns:
            str: 輸出音訊檔案路徑，失敗時返回 None
        """
        try:
            print("=" * 60)
            print("🎙️ VOAI 語音生成 (短文本)")
            print("=" * 60)
            print(f"📝 文本: {text[:50]}..." if len(text) > 50 else f"📝 文本: {text}")
            print(f"🎭 說話者: {speaker}")
            print(f"⚙️ 參數: version={version}, style={style}, speed={speed}")
            
            # 呼叫 VOAI API
            audio_bytes = self.client.speech(
                text=text,
                speaker=speaker,
                version=version,
                style=style,
                speed=speed,
                pitch_shift=pitch_shift,
                style_weight=style_weight,
                breath_pause=breath_pause,
                output_format=output_format
            )
            
            # 儲存音訊檔案
            output_dir = folder_paths.get_output_directory()
            
            # 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成唯一檔名
            output_path = get_unique_filename(output_dir, output_filename, output_format)
            
            # 寫入檔案
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ 語音生成成功: {output_path}")
            print("=" * 60)
            
            return output_path
            
        except APIError as e:
            print(f"❌ VOAI API 錯誤: {e}")
            return None
        except Exception as e:
            print(f"❌ 生成語音時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_voice(
        self,
        voai_script_text: str,
        name: str,
        model: str = "Neo",
        style: str = "預設",
        speed: float = 1.0,
        pitch_shift: int = 0,
        style_weight: float = 0.0,
        breath_pause: int = 0,
        output_format: str = "wav",
        output_filename: str = "voai_voice"
    ) -> Optional[str]:
        """
        生成長文本語音 (使用 /TTS/generate-voice endpoint)
        
        Args:
            voai_script_text (str): VOAI 腳本文本
            name (str): 說話者名稱
            model (str): 模型名稱，預設 "Neo"
            style (str): 語音風格，預設 "預設"
            speed (float): 語速，預設 1.0
            pitch_shift (int): 音調偏移，預設 0
            style_weight (float): 風格權重，預設 0.0
            breath_pause (int): 呼吸停頓，預設 0
            output_format (str): 輸出格式，預設 "wav"
            output_filename (str): 輸出檔案名稱
        
        Returns:
            str: 輸出音訊檔案路徑，失敗時返回 None
        """
        try:
            print("=" * 60)
            print("🎙️ VOAI 語音生成 (長文本)")
            print("=" * 60)
            print(f"📝 文本長度: {len(voai_script_text)} 字元")
            print(f"🎭 說話者: {name}")
            print(f"⚙️ 參數: model={model}, style={style}, speed={speed}")
            
            # 呼叫 VOAI API
            audio_bytes = self.client.generate_voice(
                voai_script_text=voai_script_text,
                name=name,
                model=model,
                style=style,
                speed=speed,
                pitch_shift=pitch_shift,
                style_weight=style_weight,
                breath_pause=breath_pause,
                output_format=output_format
            )
            
            # 儲存音訊檔案
            output_dir = folder_paths.get_output_directory()
            output_path = os.path.join(
                output_dir,
                f"{output_filename}.{output_format}"
            )
            
            # 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 寫入檔案
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ 語音生成成功: {output_path}")
            print("=" * 60)
            
            return output_path
            
        except APIError as e:
            print(f"❌ VOAI API 錯誤: {e}")
            return None
        except Exception as e:
            print(f"❌ 生成語音時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_dialogue(
        self,
        dialogue: List[Dict[str, Any]],
        preset_speakers: Optional[List[Dict[str, Any]]] = None,
        output_format: str = "wav",
        output_filename: str = "voai_dialogue"
    ) -> Optional[str]:
        """
        生成多角色對話 (使用 /TTS/generate-dialogue endpoint)
        
        Args:
            dialogue (List[Dict]): 對話列表，每個元素包含 voai_script_text 和 preset_id
            preset_speakers (List[Dict], optional): 預設說話者定義
            output_format (str): 輸出格式，預設 "wav"
            output_filename (str): 輸出檔案名稱
        
        Returns:
            str: 輸出音訊檔案路徑，失敗時返回 None
        """
        try:
            print("=" * 60)
            print("🎙️ VOAI 對話生成 (多角色)")
            print("=" * 60)
            print(f"👥 對話段落數: {len(dialogue)}")
            
            # 呼叫 VOAI API
            audio_bytes = self.client.generate_dialogue(
                dialogue=dialogue,
                preset_speakers=preset_speakers,
                output_format=output_format
            )
            
            # 儲存音訊檔案
            output_dir = folder_paths.get_output_directory()
            
            # 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成唯一檔名
            output_path = get_unique_filename(output_dir, output_filename, output_format)
            
            # 寫入檔案
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ 對話生成成功: {output_path}")
            print("=" * 60)
            
            return output_path
            
        except APIError as e:
            print(f"❌ VOAI API 錯誤: {e}")
            return None
        except Exception as e:
            print(f"❌ 生成對話時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_usage(self) -> Optional[Dict[str, Any]]:
        """
        取得 API 使用配額資訊
        
        Returns:
            Dict: 配額資訊，失敗時返回 None
        """
        try:
            print("📊 取得 API 使用情況...")
            usage = self.client.get_usage()
            print(f"✅ 使用情況: {usage}")
            return usage
        except APIError as e:
            print(f"❌ 取得使用情況時發生錯誤: {e}")
            return None
