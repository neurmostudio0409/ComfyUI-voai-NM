"""
VOAI Model Configurations
Defines VOAI TTS models and parameters
"""

VOAI_MODELS = {
    # ===== TTS Models =====
    "speech": {
        "name": "Speech",
        "display_name": "VOAI Speech (短文本)",
        "category": "audio/tts",
        "description": "短文本語音合成，適合簡短對話和提示音",
        "endpoint": "/TTS/Speech",
        "inputs": {
            "text": {"type": "STRING", "required": True, "multiline": True},
            "speaker": {"type": "STRING", "required": True, "default": "neo佑希"},
            "version": {"type": "STRING", "default": "Neo"},
            "style": {"type": "STRING", "default": "預設"},
            "speed": {"type": "FLOAT", "default": 1.0, "min": 0.5, "max": 2.0},
            "pitch_shift": {"type": "INT", "default": 0, "min": -12, "max": 12},
            "style_weight": {"type": "FLOAT", "default": 0.0, "min": 0.0, "max": 1.0},
            "breath_pause": {"type": "INT", "default": 0, "min": 0, "max": 10},
        },
        "outputs": ["audio"],
        "return_type": "AUDIO",
    },
    
    "generate-voice": {
        "name": "Generate Voice",
        "display_name": "VOAI Voice (長文本)",
        "category": "audio/tts",
        "description": "長文本語音合成，支持複雜的腳本和較長的對話",
        "endpoint": "/TTS/generate-voice",
        "inputs": {
            "voai_script_text": {"type": "STRING", "required": True, "multiline": True},
            "name": {"type": "STRING", "required": True, "default": "neo佑希"},
            "model": {"type": "STRING", "default": "Neo"},
            "style": {"type": "STRING", "default": "預設"},
            "speed": {"type": "FLOAT", "default": 1.0, "min": 0.5, "max": 2.0},
            "pitch_shift": {"type": "INT", "default": 0, "min": -12, "max": 12},
            "style_weight": {"type": "FLOAT", "default": 0.0, "min": 0.0, "max": 1.0},
            "breath_pause": {"type": "INT", "default": 0, "min": 0, "max": 10},
        },
        "outputs": ["audio"],
        "return_type": "AUDIO",
    },
    
    "generate-dialogue": {
        "name": "Generate Dialogue",
        "display_name": "VOAI Dialogue (多角色)",
        "category": "audio/tts",
        "description": "多角色對話合成，支持複雜的對話場景",
        "endpoint": "/TTS/generate-dialogue",
        "inputs": {
            "dialogue": {"type": "JSON", "required": True},
            "preset_speakers": {"type": "JSON", "required": False},
        },
        "outputs": ["audio"],
        "return_type": "AUDIO",
    },
}

# 常見說話者列表（示例）
COMMON_SPEAKERS = [
    "neo佑希",
    "neo夢夢",
    "neo綾音",
    "neo小天",
]

# 風格列表（示例）
COMMON_STYLES = [
    "預設",
    "開心",
    "悲傷",
    "生氣",
    "溫柔",
]


def get_model_config(model_id):
    """
    根據模型ID獲取配置
    
    Args:
        model_id (str): 模型識別碼
    
    Returns:
        dict: 模型配置，如果不存在則返回 None
    """
    return VOAI_MODELS.get(model_id)


def get_model_names():
    """
    獲取所有模型名稱列表
    
    Returns:
        list: 模型名稱列表
    """
    return list(VOAI_MODELS.keys())


def get_models_by_category(category):
    """
    根據類別獲取模型列表
    
    Args:
        category (str): 模型類別
    
    Returns:
        dict: 該類別的所有模型
    """
    return {
        k: v for k, v in VOAI_MODELS.items()
        if v.get("category") == category
    }