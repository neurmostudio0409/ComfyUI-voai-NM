"""
VOAI ComfyUI 節點整合
支援 VOAI TTS 語音生成服務
"""

import os
import torch
import numpy as np
from .voai_api import VoaiAPI
from .audio_utils import AudioUtils, cleanup_temp_file

# Try to import ComfyUI's folder_paths
try:
    import folder_paths
except ImportError:
    class FolderPaths:
        @staticmethod
        def get_output_directory():
            return os.path.join(os.getcwd(), "output")
    folder_paths = FolderPaths()


# 全域變數：快取說話者列表
_CACHED_SPEAKERS = None


def load_audio_as_comfyui_format(audio_path: str):
    """
    載入音訊並轉換為 ComfyUI 格式 [batch, channels, samples]
    
    Args:
        audio_path: 音訊檔案路徑
        
    Returns:
        tuple: (audio_dict, error_message) - audio_dict 包含 waveform 和 sample_rate，error_message 為錯誤訊息或 None
    """
    try:
        import soundfile as sf
        waveform, sample_rate = sf.read(audio_path)
        
        waveform_tensor = torch.from_numpy(waveform).float()
        
        print(f"🔍 調試 - 原始形狀: {waveform_tensor.shape}, 維度數: {len(waveform_tensor.shape)}")
        
        # 確保形狀為 [batch, channels, samples] 以匹配 ComfyUI 格式
        if len(waveform_tensor.shape) == 1:
            # 單聲道: [samples] -> [1, 1, samples]
            print(f"🔍 處理單聲道音訊")
            waveform_tensor = waveform_tensor.unsqueeze(0).unsqueeze(0)
            print(f"🔍 轉換後形狀: {waveform_tensor.shape}")
        elif len(waveform_tensor.shape) == 2:
            # [samples, channels] 或 [channels, samples]
            print(f"🔍 處理雙維度音訊: shape[0]={waveform_tensor.shape[0]}, shape[1]={waveform_tensor.shape[1]}")
            if waveform_tensor.shape[0] > waveform_tensor.shape[1]:
                # [samples, channels] -> [1, channels, samples]
                print(f"🔍 判斷為 [samples, channels] 格式")
                waveform_tensor = waveform_tensor.transpose(0, 1).unsqueeze(0)
            else:
                # [channels, samples] -> [1, channels, samples]
                print(f"🔍 判斷為 [channels, samples] 格式")
                waveform_tensor = waveform_tensor.unsqueeze(0)
            print(f"🔍 轉換後形狀: {waveform_tensor.shape}")
        
        audio_dict = {
            "waveform": waveform_tensor,
            "sample_rate": sample_rate
        }
        
        print(f"✅ 音訊已載入")
        print(f"   取樣率: {sample_rate}Hz")
        print(f"   最終形狀: {waveform_tensor.shape}")
        
        return audio_dict, None
        
    except Exception as e:
        error_msg = f"載入音訊時發生錯誤: {e}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return None, error_msg

def get_speaker_list():
    """獲取說話者列表，使用快取避免重複請求"""
    global _CACHED_SPEAKERS
    
    if _CACHED_SPEAKERS is not None:
        return _CACHED_SPEAKERS
    
    try:
        api = VoaiAPI()
        speakers = api.get_speakers()
        
        # 提取說話者名稱
        if isinstance(speakers, list) and len(speakers) > 0:
            speaker_names = []
            for speaker in speakers:
                if isinstance(speaker, dict) and 'name' in speaker:
                    speaker_names.append(speaker['name'])
            
            if speaker_names:
                _CACHED_SPEAKERS = speaker_names
                print(f"✅ 已載入 {len(speaker_names)} 位說話者")
                return speaker_names
    except Exception as e:
        print(f"⚠️ 無法取得說話者列表: {e}")
        import traceback
        traceback.print_exc()
    
    # 如果失敗，返回預設列表
    default_speakers = ["佑希", "夢夢", "綾音", "婉婷", "淑芬"]
    _CACHED_SPEAKERS = default_speakers
    print(f"⚠️ 使用預設說話者列表 ({len(default_speakers)} 位)")
    return default_speakers


# ======================
# VOAI TTS 節點
# ======================

class VoaiSpeechNode:
    """
    ComfyUI 節點：使用 VOAI TTS 生成短文本語音
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        speakers = get_speaker_list()
        
        return {
            "required": {
                "text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "要轉換成語音的文本"
                }),
                "speaker": (speakers, {
                    "default": speakers[0] if speakers else "佑希",
                    "tooltip": "說話者名稱"
                }),
            },
            "optional": {
                "style": ("STRING", {
                    "default": "預設",
                    "tooltip": "語音風格"
                }),
                "speed": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.5, 
                    "max": 2.0, 
                    "step": 0.1,
                    "tooltip": "語速"
                }),
                "pitch_shift": ("INT", {
                    "default": 0, 
                    "min": -12, 
                    "max": 12, 
                    "step": 1,
                    "tooltip": "音調偏移"
                }),
                "style_weight": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.1,
                    "tooltip": "風格權重"
                }),
                "breath_pause": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 10, 
                    "step": 1,
                    "tooltip": "呼吸停頓"
                }),
                "output_format": (["wav", "mp3"], {
                    "default": "wav",
                    "tooltip": "輸出音訊格式"
                }),
                "output_filename": ("STRING", {
                    "default": "voai_speech",
                    "tooltip": "輸出檔案名稱"
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_speech"
    CATEGORY = "audio/voai"
    
    def generate_speech(
        self, 
        text, 
        speaker,
        style="預設",
        speed=1.0,
        pitch_shift=0,
        style_weight=0.0,
        breath_pause=0,
        output_format="wav",
        output_filename="voai_speech"
    ):
        """生成短文本語音"""
        print("=" * 60)
        print("🎙️ VOAI 語音生成 (短文本)")
        print("=" * 60)
        
        try:
            api = VoaiAPI()
            
            audio_path = api.generate_speech(
                text=text,
                speaker=speaker,
                version="Neo",  # 固定使用 Neo
                style=style,
                speed=speed,
                pitch_shift=pitch_shift,
                style_weight=style_weight,
                breath_pause=breath_pause,
                output_format=output_format,
                output_filename=output_filename
            )
            
            if audio_path and os.path.exists(audio_path):
                print("=" * 60)
                print("✅ 語音生成完成！")
                print(f"📁 輸出: {audio_path}")
                print("=" * 60)
                
                # 載入音訊 - 使用統一的格式轉換函數
                audio_dict, error = load_audio_as_comfyui_format(audio_path)
                if audio_dict:
                    return (audio_dict,)
                else:
                    return (None,)
            else:
                print("=" * 60)
                print("❌ 語音生成失敗！")
                print("=" * 60)
                return (None,)
                
        except ValueError as e:
            print(f"❌ API 初始化失敗: {str(e)}")
            print("\n請確保：")
            print("1. 在 .env 檔案中設定 VOAI_API_KEY")
            print("2. 從 VOAI 官網取得 API key")
            return (None,)
        except Exception as e:
            print(f"❌ 生成時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return (None,)


class VoaiVoiceNode:
    """
    ComfyUI 節點：使用 VOAI TTS 生成長文本語音
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        speakers = get_speaker_list()
        
        return {
            "required": {
                "voai_script_text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "VOAI 腳本文本（支持長文本）"
                }),
                "speaker_name": (speakers, {
                    "default": speakers[0] if speakers else "佑希",
                    "tooltip": "說話者名稱"
                }),
            },
            "optional": {
                "style": ("STRING", {
                    "default": "預設",
                    "tooltip": "語音風格"
                }),
                "speed": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.5, 
                    "max": 2.0, 
                    "step": 0.1,
                    "tooltip": "語速"
                }),
                "pitch_shift": ("INT", {
                    "default": 0, 
                    "min": -12, 
                    "max": 12, 
                    "step": 1,
                    "tooltip": "音調偏移"
                }),
                "style_weight": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.1,
                    "tooltip": "風格權重"
                }),
                "breath_pause": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 10, 
                    "step": 1,
                    "tooltip": "呼吸停頓"
                }),
                "output_format": (["wav", "mp3"], {
                    "default": "wav",
                    "tooltip": "輸出音訊格式"
                }),
                "output_filename": ("STRING", {
                    "default": "voai_voice",
                    "tooltip": "輸出檔案名稱"
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_voice"
    CATEGORY = "audio/voai"
    
    def generate_voice(
        self, 
        voai_script_text, 
        speaker_name,
        style="預設",
        speed=1.0,
        pitch_shift=0,
        style_weight=0.0,
        breath_pause=0,
        output_format="wav",
        output_filename="voai_voice"
    ):
        """生成長文本語音"""
        print("=" * 60)
        print("🎙️ VOAI 語音生成 (長文本)")
        print("=" * 60)
        
        try:
            api = VoaiAPI()
            
            audio_path = api.generate_voice(
                voai_script_text=voai_script_text,
                name=speaker_name,
                model="Neo",  # 固定使用 Neo
                style=style,
                speed=speed,
                pitch_shift=pitch_shift,
                style_weight=style_weight,
                breath_pause=breath_pause,
                output_format=output_format,
                output_filename=output_filename
            )
            
            if audio_path and os.path.exists(audio_path):
                print("=" * 60)
                print("✅ 語音生成完成！")
                print(f"📁 輸出: {audio_path}")
                print("=" * 60)
                
                # 載入音訊
                audio_dict, error = load_audio_as_comfyui_format(audio_path)
                if audio_dict:
                    return (audio_dict,)
                else:
                    return (None,)
            else:
                print("=" * 60)
                print("❌ 語音生成失敗！")
                print("=" * 60)
                return (None,)
                
        except ValueError as e:
            print(f"❌ API 初始化失敗: {str(e)}")
            print("\n請確保：")
            print("1. 在 .env 檔案中設定 VOAI_API_KEY")
            print("2. 從 VOAI 官網取得 API key")
            return (None,)
        except Exception as e:
            print(f"❌ 生成時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return (None,)


class VoaiDialogueNode:
    """
    ComfyUI 節點：使用 VOAI TTS 生成多角色對話（友善輸入）
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        speakers = get_speaker_list()
        
        return {
            "required": {
                "line_1_text": ("STRING", {
                    "default": "你好！今天天氣真好。", 
                    "multiline": True,
                    "tooltip": "第1句對話文本"
                }),
                "line_1_speaker": (speakers, {
                    "default": speakers[0] if speakers else "佑希",
                    "tooltip": "第1句說話者"
                }),
            },
            "optional": {
                "line_2_text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "第2句對話文本（選填）"
                }),
                "line_2_speaker": (speakers, {
                    "default": speakers[1] if len(speakers) > 1 else speakers[0] if speakers else "夢夢",
                    "tooltip": "第2句說話者"
                }),
                "line_3_text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "第3句對話文本（選填）"
                }),
                "line_3_speaker": (speakers, {
                    "default": speakers[0] if speakers else "佑希",
                    "tooltip": "第3句說話者"
                }),
                "line_4_text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "第4句對話文本（選填）"
                }),
                "line_4_speaker": (speakers, {
                    "default": speakers[1] if len(speakers) > 1 else speakers[0] if speakers else "夢夢",
                    "tooltip": "第4句說話者"
                }),
                "line_5_text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "第5句對話文本（選填）"
                }),
                "line_5_speaker": (speakers, {
                    "default": speakers[0] if speakers else "佑希",
                    "tooltip": "第5句說話者"
                }),
                "output_format": (["wav", "mp3"], {
                    "default": "wav",
                    "tooltip": "輸出音訊格式"
                }),
                "output_filename": ("STRING", {
                    "default": "voai_dialogue",
                    "tooltip": "輸出檔案名稱"
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_dialogue"
    CATEGORY = "audio/voai"
    
    def generate_dialogue(
        self, 
        line_1_text,
        line_1_speaker,
        line_2_text="",
        line_2_speaker="夢夢",
        line_3_text="",
        line_3_speaker="佑希",
        line_4_text="",
        line_4_speaker="夢夢",
        line_5_text="",
        line_5_speaker="佑希",
        output_format="wav",
        output_filename="voai_dialogue"
    ):
        """生成多角色對話"""
        print("=" * 60)
        print("🎙️ VOAI 對話生成 (多角色)")
        print("=" * 60)
        
        try:
            api = VoaiAPI()
            
            # 構建對話列表
            dialogue = []
            
            # 添加第1句（必填）
            if line_1_text.strip():
                dialogue.append({
                    "voai_script_text": line_1_text,
                    "preset_id": line_1_speaker
                })
            
            # 添加第2-5句（選填）
            if line_2_text.strip():
                dialogue.append({
                    "voai_script_text": line_2_text,
                    "preset_id": line_2_speaker
                })
            
            if line_3_text.strip():
                dialogue.append({
                    "voai_script_text": line_3_text,
                    "preset_id": line_3_speaker
                })
            
            if line_4_text.strip():
                dialogue.append({
                    "voai_script_text": line_4_text,
                    "preset_id": line_4_speaker
                })
            
            if line_5_text.strip():
                dialogue.append({
                    "voai_script_text": line_5_text,
                    "preset_id": line_5_speaker
                })
            
            if not dialogue:
                print("❌ 沒有提供對話內容")
                return (None,)
            
            print(f"👥 對話段落數: {len(dialogue)}")
            
            audio_path = api.generate_dialogue(
                dialogue=dialogue,
                preset_speakers=None,
                output_format=output_format,
                output_filename=output_filename
            )
            
            if audio_path and os.path.exists(audio_path):
                print("=" * 60)
                print("✅ 對話生成完成！")
                print(f"📁 輸出: {audio_path}")
                print("=" * 60)
                
                # 載入音訊
                audio_dict, error = load_audio_as_comfyui_format(audio_path)
                if audio_dict:
                    return (audio_dict,)
                else:
                    return (None,)
            else:
                print("=" * 60)
                print("❌ 對話生成失敗！")
                print("=" * 60)
                return (None,)
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析錯誤: {e}")
            print("請確保輸入的是有效的 JSON 格式")
            return (None,)
        except ValueError as e:
            print(f"❌ API 初始化失敗: {str(e)}")
            print("\n請確保：")
            print("1. 在 .env 檔案中設定 VOAI_API_KEY")
            print("2. 從 VOAI 官網取得 API key")
            return (None,)
        except Exception as e:
            print(f"❌ 生成時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return (None,)


class VoaiGetSpeakersNode:
    """
    ComfyUI 節點：取得 VOAI 可用的說話者列表
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("speakers_info",)
    FUNCTION = "get_speakers"
    CATEGORY = "audio/voai"
    OUTPUT_NODE = True
    
    def get_speakers(self):
        """取得說話者列表"""
        print("=" * 60)
        print("📋 取得 VOAI 說話者列表")
        print("=" * 60)
        
        try:
            api = VoaiAPI()
            speakers = api.get_speakers()
            
            if speakers:
                import json
                speakers_text = json.dumps(speakers, ensure_ascii=False, indent=2)
                print(speakers_text)
                return (speakers_text,)
            else:
                return ("❌ 無法取得說話者列表",)
                
        except ValueError as e:
            error_msg = f"❌ API 初始化失敗: {str(e)}\n\n請確保：\n1. 在 .env 檔案中設定 VOAI_API_KEY\n2. 從 VOAI 官網取得 API key"
            print(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"❌ 錯誤: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg,)


class VoaiGetUsageNode:
    """
    ComfyUI 節點：取得 VOAI API 使用配額
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("usage_info",)
    FUNCTION = "get_usage"
    CATEGORY = "audio/voai"
    OUTPUT_NODE = True
    
    def get_usage(self):
        """取得 API 使用配額"""
        print("=" * 60)
        print("📊 取得 VOAI API 使用情況")
        print("=" * 60)
        
        try:
            api = VoaiAPI()
            usage = api.get_usage()
            
            if usage:
                import json
                usage_text = json.dumps(usage, ensure_ascii=False, indent=2)
                print(usage_text)
                return (usage_text,)
            else:
                return ("❌ 無法取得使用情況",)
                
        except ValueError as e:
            error_msg = f"❌ API 初始化失敗: {str(e)}\n\n請確保：\n1. 在 .env 檔案中設定 VOAI_API_KEY\n2. 從 VOAI 官網取得 API key"
            print(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"❌ 錯誤: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg,)


# ======================
# 節點註冊
# ======================

NODE_CLASS_MAPPINGS = {
    "VoaiSpeechNode": VoaiSpeechNode,
    "VoaiVoiceNode": VoaiVoiceNode,
    "VoaiDialogueNode": VoaiDialogueNode,
    "VoaiGetSpeakersNode": VoaiGetSpeakersNode,
    "VoaiGetUsageNode": VoaiGetUsageNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VoaiSpeechNode": "🎙️ VOAI 語音 / Speech (短文本)",
    "VoaiVoiceNode": "🎙️ VOAI 語音 / Voice (長文本)",
    "VoaiDialogueNode": "👥 VOAI 對話 / Dialogue (多角色)",
    "VoaiGetSpeakersNode": "📋 VOAI 說話者列表 / Get Speakers",
    "VoaiGetUsageNode": "📊 VOAI 使用情況 / Get Usage",
}
