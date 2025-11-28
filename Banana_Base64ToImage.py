import base64
import io
import torch
import numpy as np
from PIL import Image
import re

class BananaBase64ToImage:
    """
    Banana版本的Base64转图像节点
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_string": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "粘贴base64编码或包含base64的文本"
                }),
            },
            "optional": {
                "mode": (["auto", "RGB", "RGBA"], {
                    "default": "auto"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "info")
    FUNCTION = "decode_base64"
    CATEGORY = "🍌 Banana/Image"
    OUTPUT_NODE = False

    def decode_base64(self, base64_string, mode="auto"):
        """
        从文本中提取Base64编码并解码为图像
        """
        if not base64_string.strip():
            raise ValueError("输入文本不能为空")

        try:
            # 从混合文本中提取base64编码
            clean_base64_data = self.extract_base64_from_text(base64_string)

            if not clean_base64_data:
                raise ValueError("未在文本中找到有效的base64图像编码")

            # 解码Base64
            image_data = base64.b64decode(clean_base64_data)

            # 使用PIL打开图像
            image = Image.open(io.BytesIO(image_data))

            # 处理图像模式
            image, has_alpha = self.process_image_mode(image, mode)

            # 转换为ComfyUI格式
            image_tensor = self.pil_to_tensor(image)

            # 生成掩码
            mask_tensor = self.generate_mask(image, has_alpha)

            info_text = f"解码成功: {image.size[0]}x{image.size[1]}, 模式: {image.mode}"

            return (image_tensor, mask_tensor, info_text)

        except Exception as e:
            error_msg = f"Base64解码失败: {str(e)}"
            raise ValueError(error_msg)

    def extract_base64_from_text(self, text):
        """从混合文本中提取base64编码部分"""
        # 移除所有空白字符
        clean_text = re.sub(r'\s+', '', text)

        # 模式1: 匹配data URI格式
        data_uri_pattern = r'data:image/(?:png|jpeg|jpg|gif|webp);base64,([A-Za-z0-9+/=]+)'
        data_uri_match = re.search(data_uri_pattern, clean_text)

        if data_uri_match:
            return data_uri_match.group(1)

        # 模式2: 匹配长base64字符串
        base64_pattern = r'([A-Za-z0-9+/]{100,}={0,2})'
        base64_matches = re.findall(base64_pattern, clean_text)

        if base64_matches:
            base64_matches.sort(key=len, reverse=True)
            longest_match = base64_matches[0]
            try:
                base64.b64decode(longest_match)
                return longest_match
            except:
                pass

        # 模式3: 查找base64,前缀
        try:
            base64_index = clean_text.find('base64,')
            if base64_index != -1:
                potential_base64 = clean_text[base64_index + 7:]
                base64.b64decode(potential_base64)
                return potential_base64
        except:
            pass

        # 最后尝试直接解码整个文本
        try:
            base64.b64decode(clean_text)
            return clean_text
        except:
            pass

        return None

    def process_image_mode(self, image, mode):
        """处理图像模式和转换"""
        original_mode = image.mode
        has_alpha = original_mode in ('RGBA', 'LA', 'PA')

        if mode != "auto":
            if mode == "RGB" and has_alpha:
                image = image.convert('RGB')
                has_alpha = False
            elif mode == "RGBA" and not has_alpha:
                image = image.convert('RGBA')
                has_alpha = True
            else:
                image = image.convert(mode)
        else:
            # 自动模式处理
            if original_mode == 'P':
                image = image.convert('RGBA' if image.info.get('transparency') else 'RGB')
                has_alpha = image.mode == 'RGBA'
            elif original_mode in ('LA', 'PA'):
                image = image.convert('RGBA')
                has_alpha = True
            elif original_mode != 'RGB' and original_mode != 'RGBA':
                image = image.convert('RGB')
                has_alpha = False

        return image, has_alpha

    def pil_to_tensor(self, image):
        """PIL图像转换为ComfyUI张量"""
        image_array = np.array(image).astype(np.float32) / 255.0

        # 处理单通道图像
        if len(image_array.shape) == 2:
            image_array = np.expand_dims(image_array, axis=-1)

        # 转换为 (1, H, W, C) 格式
        if image_array.shape[-1] == 1:
            image_tensor = torch.from_numpy(image_array).unsqueeze(0)
        else:
            image_tensor = torch.from_numpy(image_array)[None,]

        return image_tensor

    def generate_mask(self, image, has_alpha):
        """从图像生成掩码"""
        if has_alpha and image.mode == 'RGBA':
            # 提取Alpha通道作为掩码
            alpha_array = np.array(image.split()[-1]).astype(np.float32) / 255.0
            mask_tensor = torch.from_numpy(alpha_array).unsqueeze(0).unsqueeze(-1)
        else:
            # 创建全白掩码
            width, height = image.size
            mask_tensor = torch.ones((1, height, width, 1), dtype=torch.float32)

        return mask_tensor

# ComfyUI节点映射 - 这是关键部分！
NODE_CLASS_MAPPINGS = {
    "BananaBase64ToImage": BananaBase64ToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BananaBase64ToImage": "🍌 Base64 to Image",
}