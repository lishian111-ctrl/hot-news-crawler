"""
翻译和 AI 总结路由
提供英文翻译、AI 内容总结等 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from loguru import logger
import httpx

router = APIRouter(prefix="/translate", tags=["翻译与 AI 总结"])


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "zh"


class TranslateResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str


class SummaryRequest(BaseModel):
    text: str
    max_length: int = 200


class SummaryResponse(BaseModel):
    summary: str


# 简单的中英文检测
def detect_language(text: str) -> str:
    """检测文本语言"""
    if not text:
        return "unknown"

    # 计算英文字符比例
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total_chars = len(text.replace(" ", "").replace("\n", ""))

    if total_chars == 0:
        return "unknown"

    english_ratio = english_chars / total_chars

    # 英文字符占比超过 50% 认为是英文
    if english_ratio > 0.5:
        return "en"

    # 检查是否包含中文字符
    if any("\u4e00" <= c <= "\u9fff" for c in text):
        return "zh"

    return "unknown"


# 使用免费的翻译 API（可以根据需要替换为其他翻译服务）
async def translate_text(text: str, target_lang: str = "zh") -> str:
    """翻译文本"""
    if not text:
        return text

    # 检测源语言
    source_lang = detect_language(text)

    # 如果已经是中文，直接返回
    if source_lang == "zh":
        return text

    try:
        # 使用 MyMemory 翻译 API（免费，无需 API key）
        # 注意：生产环境建议替换为百度翻译、有道翻译或 DeepL 等更稳定的服务
        api_url = f"https://api.mymemory.translated.net/get"
        params = {
            "q": text[:500],  # 限制长度
            "langpair": f"{source_lang}|{target_lang}"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("responseStatus") == 200:
                return data.get("responseData", {}).get("translatedText", text)
            else:
                logger.warning(f"翻译 API 返回错误：{data.get('responseDetails')}")
                return text

    except Exception as e:
        logger.error(f"翻译失败：{e}")
        return text


# 简单的 AI 总结（基于文本提取）
# 注意：这是基础版本，生产环境建议接入真正的 AI 服务（如文心一言、通义千问等）
async def generate_summary(text: str, max_length: int = 200) -> str:
    """生成文本摘要"""
    if not text:
        return ""

    # 如果文本本身就很短，直接返回
    if len(text) <= max_length:
        return text

    # 简单的提取式摘要
    # 按句子分割
    sentences = []
    for delimiter in ['.', '!', '?', '\n', '。', '！', '？']:
        text = text.replace(delimiter, '\n')
    sentences = [s.strip() for s in text.split('\n') if s.strip()]

    if not sentences:
        return text[:max_length] + "..."

    # 提取关键句子（基于位置和长度）
    summary_parts = []
    current_length = 0

    # 优先取前几句和包含关键词的句子
    keywords = ['重要', '关键', '主要', '发现', '结果', '显示', '表明', '首次', '突破', '发布']

    for i, sentence in enumerate(sentences):
        if current_length >= max_length:
            break

        # 前两句优先
        if i < 2:
            summary_parts.append(sentence)
            current_length += len(sentence)
        else:
            # 包含关键词的句子
            for kw in keywords:
                if kw in sentence:
                    summary_parts.append(sentence)
                    current_length += len(sentence)
                    break

    if not summary_parts:
        # 如果没有找到关键句，取前几句
        summary_parts = sentences[:3]

    summary = ' '.join(summary_parts)

    # 确保不超过最大长度
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."

    return summary


@router.post("/translate", summary="翻译文本")
async def translate_endpoint(request: TranslateRequest):
    """
    翻译文本，支持自动检测源语言
    """
    try:
        # 检测语言
        source_lang = detect_language(request.text)

        # 如果已经是目标语言，直接返回
        if source_lang == request.target_language:
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "translated_text": request.text,
                    "source_language": source_lang,
                    "target_language": request.target_language
                }
            }

        # 翻译
        translated = await translate_text(request.text, request.target_language)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "translated_text": translated,
                "source_language": source_lang,
                "target_language": request.target_language
            }
        }
    except Exception as e:
        logger.error(f"翻译失败：{e}")
        raise HTTPException(status_code=500, detail=f"翻译失败：{str(e)}")


@router.post("/summary", summary="AI 总结")
async def summary_endpoint(request: SummaryRequest):
    """
    对文本进行 AI 总结
    """
    try:
        summary = await generate_summary(request.text, request.max_length)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "summary": summary
            }
        }
    except Exception as e:
        logger.error(f"生成摘要失败：{e}")
        raise HTTPException(status_code=500, detail=f"生成摘要失败：{str(e)}")


@router.get("/detect-language", summary="检测语言")
async def detect_language_endpoint(text: str):
    """
    检测文本语言
    """
    lang = detect_language(text)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "language": lang
        }
    }
