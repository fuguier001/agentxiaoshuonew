from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
import logging
import tempfile
import os
import httpx

from app.services.learning_service import get_learning_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["学习系统"])


@router.post("/learning/analyze")
async def analyze_work(analysis_data: Dict[str, Any]):
    try:
        result = await get_learning_service().analyze_work(analysis_data)
        return {"status": "success", "data": result, "message": "作品分析完成"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"分析作品失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    work = get_learning_service().get_analysis_status(analysis_id)
    if not work:
        raise HTTPException(status_code=404, detail=f"分析不存在：{analysis_id}")
    return {"status": "success", "data": work}


@router.get("/learning/works")
async def list_analyzed_works():
    return {"status": "success", "data": get_learning_service().list_analyzed_works()}


@router.delete("/learning/works/{analysis_id}")
async def delete_analyzed_work(analysis_id: str):
    if not get_learning_service().delete_analyzed_work(analysis_id):
        raise HTTPException(status_code=404, detail=f"分析不存在：{analysis_id}")
    return {"status": "success", "message": f"已删除分析：{analysis_id}"}


@router.get("/learning/works/{analysis_id}")
async def get_work_detail(analysis_id: str):
    work = get_learning_service().get_work_detail(analysis_id)
    if not work:
        raise HTTPException(status_code=404, detail=f"分析不存在：{analysis_id}")
    return {"status": "success", "data": work}


@router.get("/learning/report")
async def get_learning_report(project_id: str = "default"):
    try:
        report = get_learning_service().get_learning_report(project_id)
        return {"status": "success", "data": report}
    except Exception as e:
        logger.error(f"获取学习报告失败：{e}")
        return {"status": "success", "data": {"project_id": project_id, "analyzed_works": 0, "style_features_learned": 0, "techniques_mastered": 0, "chapters_evaluated": 0, "average_score": 0.0, "recommendations": ["暂无数据"]}}


# ========== 文件转换相关 ==========

# 每段最大字符数
MAX_SEGMENT_SIZE = 10000


@router.post("/learning/convert/file")
async def convert_file_to_text(
    file: UploadFile = File(...),
    segment_size: int = Form(default=MAX_SEGMENT_SIZE)
):
    """
    上传文件并转换为文字

    支持格式: txt, md, pdf, doc, docx
    自动分段返回
    """
    try:
        # 获取文件扩展名
        filename = file.filename or "unknown"
        ext = os.path.splitext(filename)[1].lower()

        # 支持的格式
        supported_formats = ['.txt', '.md', '.pdf', '.doc', '.docx']
        if ext not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式：{ext}。支持：{', '.join(supported_formats)}"
            )

        # 读取文件内容
        content = await file.read()

        # 根据格式转换
        if ext in ['.txt', '.md']:
            text = content.decode('utf-8', errors='ignore')
        elif ext == '.pdf':
            text = await _convert_pdf(content)
        elif ext in ['.doc', '.docx']:
            text = await _convert_word(content, ext)
        else:
            raise HTTPException(status_code=400, detail=f"无法处理格式：{ext}")

        # 自动分段
        segments = _segment_text(text, segment_size)

        return {
            "status": "success",
            "data": {
                "filename": filename,
                "total_chars": len(text),
                "segment_count": len(segments),
                "segments": segments
            },
            "message": f"文件转换成功，共 {len(text)} 字符，分为 {len(segments)} 段"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件转换失败：{e}")
        raise HTTPException(status_code=500, detail=f"文件转换失败：{str(e)}")


@router.post("/learning/convert/url")
async def convert_url_to_text(
    url: str = Form(...),
    segment_size: int = Form(default=MAX_SEGMENT_SIZE)
):
    """
    从 URL 获取内容并转换为文字

    支持网页和在线文档
    """
    try:
        # 验证 URL
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="无效的 URL 格式")

        # 获取内容
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')

        # 根据内容类型处理
        if 'pdf' in content_type or url.lower().endswith('.pdf'):
            text = await _convert_pdf(response.content)
        elif 'word' in content_type or url.lower().endswith(('.doc', '.docx')):
            ext = '.docx' if url.lower().endswith('.docx') else '.doc'
            text = await _convert_word(response.content, ext)
        else:
            # 网页内容，提取正文
            text = _extract_web_text(response.text, url)

        # 自动分段
        segments = _segment_text(text, segment_size)

        return {
            "status": "success",
            "data": {
                "url": url,
                "total_chars": len(text),
                "segment_count": len(segments),
                "segments": segments
            },
            "message": f"URL 内容获取成功，共 {len(text)} 字符，分为 {len(segments)} 段"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"无法访问 URL：{e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"网络请求失败：{str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL 转换失败：{e}")
        raise HTTPException(status_code=500, detail=f"URL 转换失败：{str(e)}")


# ========== 转换辅助函数 ==========

async def _convert_pdf(content: bytes) -> str:
    """转换 PDF 文件"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF 转换需要安装 PyMuPDF: pip install pymupdf"
        )

    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 解析失败：{str(e)}")


async def _convert_word(content: bytes, ext: str) -> str:
    """转换 Word 文件"""
    try:
        import docx
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Word 转换需要安装 python-docx: pip install python-docx"
        )

    try:
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            doc = docx.Document(tmp_path)
            text_parts = [para.text for para in doc.paragraphs]
            return "\n\n".join(text_parts)
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word 解析失败：{str(e)}")


def _extract_web_text(html_content: str, url: str) -> str:
    """从网页提取正文"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        # 简单提取：移除 HTML 标签
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # 获取正文
        text = soup.get_text(separator='\n')

        # 清理多余空白
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)
    except Exception as e:
        logger.warning(f"网页解析失败，使用简单提取：{e}")
        # 回退到简单提取
        import re
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def _segment_text(text: str, max_size: int = MAX_SEGMENT_SIZE) -> list:
    """
    将长文本分段

    优先在段落边界分段，避免截断句子
    """
    if len(text) <= max_size:
        return [text]

    segments = []
    paragraphs = text.split('\n\n')
    current_segment = ""

    for para in paragraphs:
        # 如果当前段落本身超长，需要按句子分割
        if len(para) > max_size:
            # 先保存当前段落
            if current_segment:
                segments.append(current_segment.strip())
                current_segment = ""

            # 按句子分割超长段落
            sentences = _split_sentences(para)
            for sentence in sentences:
                if len(current_segment) + len(sentence) + 1 <= max_size:
                    current_segment += sentence + "\n"
                else:
                    if current_segment:
                        segments.append(current_segment.strip())
                    current_segment = sentence + "\n"
        else:
            # 正常段落
            if len(current_segment) + len(para) + 2 <= max_size:
                current_segment += para + "\n\n"
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = para + "\n\n"

    # 添加最后一段
    if current_segment:
        segments.append(current_segment.strip())

    return segments


def _split_sentences(text: str) -> list:
    """按句子分割文本"""
    import re
    # 中文和英文句子结束符
    pattern = r'(?<=[。！？.!?])\s*'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]
