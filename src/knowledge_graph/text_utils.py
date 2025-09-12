import jieba


""" Text processing utilities for the knowledge graph generator.
"""

# 切分英文
# def chunk_text(text, chunk_size=500, overlap=50):
#     """ Split a text into chunks of words with overlap.
#     Args:
#         text: The input text to chunk
#         chunk_size: The size of each chunk in words
#         overlap: The number of words to overlap between chunks
#     Returns:
#         List of text chunks
#     """
#     # Split text into words
#     words = text.split()
    
#     # If text is smaller than chunk size, return it as a single chunk
#     if len(words) <= chunk_size:
#         return [text]
    
#     # Create chunks with overlap
#     chunks,start = [], 0
#     while start < len(words):
#         # Calculate end position for this chunk
#         end = min(start + chunk_size, len(words))
#         # Join words for this chunk
#         chunk = ' '.join(words[start:end])
#         chunks.append(chunk)
#         # Move start position for next chunk, accounting for overlap
#         start = end - overlap
#         # If we're near the end and the last chunk would be too small, just exit
#         if start < len(words) and start + chunk_size - overlap >= len(words):
#             # Add remaining words as the final chunk
#             final_chunk = ' '.join(words[start:])
#             chunks.append(final_chunk)
#             break
    
#     return chunks 



def chunk_text(text, chunk_size=2000, overlap=200, max_chunks=500):  
    """ 安全中文切分（确保每段有足够词数）：  
    - chunk_size: 每段字符数，增大可以得到更长片段  
    - overlap: 前后段重叠字符数  
    - max_chunks: 最大段数，避免远程机卡死  
    """  
    if overlap >= chunk_size:  
        raise ValueError("overlap 必须小于 chunk_size")  
  
    chunks = []  
    start = 0  
    text_len = len(text)  
      
    # 增加最小词数检查  
    min_words_per_chunk = 50  # 确保每个块至少有50个词  
  
    while start < text_len and len(chunks) < max_chunks:  
        end = min(start + chunk_size, text_len)  
        chunk = text[start:end]  
          
        # 检查词数，如果太少就扩大块  
        word_count = len(chunk.split())  
        if word_count < min_words_per_chunk and end < text_len:  
            # 扩大到至少包含足够词数  
            words_needed = min_words_per_chunk - word_count  
            additional_chars = words_needed * 5  # 估算每个词平均5个字符  
            end = min(start + chunk_size + additional_chars, text_len)  
            chunk = text[start:end]  
          
        chunks.append(chunk)  
        if end == text_len:  
            break  
        start = end - overlap  
        if start < 0:  
            start = 0  
  
    if start < text_len:  
        print(f"⚠️ 文本过长，仅切分了前 {max_chunks} 段，其余被截断。")  
  
    return chunks