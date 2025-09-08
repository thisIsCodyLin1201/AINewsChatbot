"""
文章摘要生成模組
實作 Lead-3 演算法，取前三句話作為摘要
"""
import re


def summarize_article(content, max_length=280):
    """
    使用 Lead-3 方法生成文章摘要
    
    Args:
        content (str): 文章內容
        max_length (int): 摘要最大長度，預設 280 字
        
    Returns:
        str: 文章摘要
    """
    if not content:
        return ""
    
    # 清理內容
    content = clean_content(content)
    
    # 使用 Lead-3 演算法
    summary = lead_3_summary(content)
    
    # 限制長度
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit('。', 1)[0] + "。"
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
    
    return summary


def lead_3_summary(content):
    """
    Lead-3 演算法：取前三句話作為摘要
    
    Args:
        content (str): 文章內容
        
    Returns:
        str: 前三句話組成的摘要
    """
    # 分句的正則表達式（中文句號、問號、驚嘆號）
    sentences = re.split(r'[。！？]', content)
    
    # 過濾空句子和過短的句子
    valid_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 5:  # 至少 5 個字才算有效句子
            valid_sentences.append(sentence)
    
    # 取前三句
    lead_sentences = valid_sentences[:3]
    
    # 重新組合，加上句號
    if lead_sentences:
        summary = '。'.join(lead_sentences) + '。'
    else:
        # 如果沒有找到有效句子，返回前 100 個字
        summary = content[:100] + "..." if len(content) > 100 else content
    
    return summary


def clean_content(content):
    """
    清理文章內容
    
    Args:
        content (str): 原始內容
        
    Returns:
        str: 清理後的內容
    """
    # 移除多餘空白
    content = re.sub(r'\s+', ' ', content)
    
    # 移除首尾空白
    content = content.strip()
    
    return content


def extract_first_paragraph(content, max_length=200):
    """
    提取第一段作為摘要（備用方法）
    
    Args:
        content (str): 文章內容
        max_length (int): 最大長度
        
    Returns:
        str: 第一段摘要
    """
    if not content:
        return ""
    
    # 按段落分割
    paragraphs = content.split('\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if len(paragraph) > 20:  # 找到第一個有意義的段落
            if len(paragraph) <= max_length:
                return paragraph
            else:
                # 截斷到合適長度，在句號處截斷
                truncated = paragraph[:max_length]
                last_period = truncated.rfind('。')
                if last_period > max_length * 0.7:  # 至少保留 70% 的內容
                    return truncated[:last_period + 1]
                else:
                    return truncated + "..."
    
    return content[:max_length] + "..." if len(content) > max_length else content


def test_summarize():
    """
    測試摘要功能
    """
    test_content = """
    這是一篇測試文章的第一句話。這是第二句話，用來測試摘要功能。
    第三句話是為了驗證 Lead-3 演算法的效果。第四句話不應該出現在摘要中。
    第五句話也不應該出現。這是最後一句話。
    """
    
    summary = summarize_article(test_content)
    print("測試內容：")
    print(test_content)
    print("\nLead-3 摘要：")
    print(summary)
    print(f"\n摘要長度：{len(summary)} 字")


if __name__ == "__main__":
    test_summarize()
