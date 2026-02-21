import os
import logging
from pypdf import PdfReader, PdfWriter
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class PdfSplitter:
    @staticmethod
    def _process_outline_item(item, outlines, parent_level=0):
        """
        递归处理大纲项，支持嵌套结构和合并生成的大纲
        返回格式: [(title, page_number, level), ...] (page_number为0-based)
        """
        if isinstance(item, tuple):
            if len(item) == 2:
                # 标准大纲项格式: (title, destination)
                title, destination = item
                page_num = None
                
                # 处理不同类型的目的地
                if hasattr(destination, 'page_number'):
                    # 直接是页面目标
                    page_num = destination.page_number  # 0-based
                elif isinstance(destination, list) and destination:
                    # 目的地是列表，尝试获取第一个元素的页码
                    first_dest = destination[0]
                    if hasattr(first_dest, 'page_number'):
                        page_num = first_dest.page_number
                elif isinstance(destination, int):
                    # 直接是页码（某些特殊情况）
                    page_num = destination
                
                if page_num is not None:
                    outlines.append((title, page_num, parent_level))
            elif len(item) == 3:
                # 嵌套大纲项格式: (title, [(destination_type, ..., page_num), ...], ...)
                title, destination_list, _ = item
                if destination_list and isinstance(destination_list, list):
                    # 提取页码信息
                    for dest in destination_list:
                        if isinstance(dest, (list, tuple)) and len(dest) > 0:
                            # 查找页码元素
                            for elem in dest:
                                if isinstance(elem, int):
                                    page_num = elem
                                    outlines.append((title, page_num, parent_level))
                                    break
                                elif hasattr(elem, 'page_number'):
                                    page_num = elem.page_number
                                    outlines.append((title, page_num, parent_level))
                                    break
                            if page_num is not None:
                                break
        elif isinstance(item, list):
            # 嵌套大纲列表，递归处理每个子项
            for subitem in item:
                PdfSplitter._process_outline_item(subitem, outlines, parent_level)
        elif hasattr(item, '__iter__') and not isinstance(item, (str, bytes)):
            # 其他可迭代对象，尝试递归处理
            for subitem in item:
                PdfSplitter._process_outline_item(subitem, outlines, parent_level)
        elif hasattr(item, 'title') and hasattr(item, 'page_number'):
            # 直接是大纲项对象
            outlines.append((item.title, item.page_number, parent_level))
    
    @staticmethod
    def _get_outlines(reader) -> List[Tuple[str, int, int]]:
        """
        获取PDF文件的大纲信息，支持嵌套结构
        适配PdfMerger.merge方法添加的书签
        返回格式: [(title, page_number, level), ...] (page_number为0-based, level为大纲层级)
        """
        outlines = []
        
        # 尝试使用不同的方法获取大纲
        try:
            # 方法1：直接访问reader.outline
            if hasattr(reader, 'outline') and reader.outline:
                # 遍历所有顶级大纲项，递归处理
                for item in reader.outline:
                    PdfSplitter._process_outline_item(item, outlines)
        except Exception as e:
            logger.error(f"获取大纲时出错: {e}")
        
        # 如果方法1失败，尝试方法2：直接访问reader._get_outlines()
        if not outlines:
            try:
                if hasattr(reader, '_get_outlines'):
                    raw_outlines = reader._get_outlines()
                    for outline in raw_outlines:
                        PdfSplitter._process_outline_item(outline, outlines)
            except Exception as e:
                logger.error(f"使用_get_outlines获取大纲时出错: {e}")
        
        # 如果方法2失败，尝试方法3：直接访问reader._outlines
        if not outlines:
            try:
                if hasattr(reader, '_outlines') and reader._outlines:
                    for outline in reader._outlines:
                        PdfSplitter._process_outline_item(outline, outlines)
            except Exception as e:
                logger.error(f"访问_outlines获取大纲时出错: {e}")
        
        return outlines
    
    @staticmethod
    def _add_outlines(writer, outlines, start_page, end_page):
        """
        向PDF写入器添加大纲，支持嵌套结构
        只添加指定页码范围内的大纲项
        兼容合并生成的大纲格式
        """
        if not outlines:
            return
        
        # 按页码和层级排序大纲项
        sorted_outlines = sorted(outlines, key=lambda x: (x[1], x[2]))
        
        # 创建大纲字典，用于记录不同层级的父大纲
        outline_parents = {0: None}  # 初始层级为0，父大纲为None
        
        # 跟踪上一个大纲项的层级，用于处理嵌套关系
        last_level = 0
        
        for title, page_num, level in sorted_outlines:
            if start_page <= page_num < end_page:
                # 计算相对页码
                relative_page = page_num - start_page
                
                # 确保层级的连续性，处理可能的层级跳跃
                if level > last_level + 1:
                    # 如果当前层级比上一个层级大2或更多，调整为上一个层级+1
                    level = last_level + 1
                
                # 确保父大纲存在，如果不存在则使用更高级别的父大纲
                while level - 1 not in outline_parents and level > 0:
                    level -= 1
                
                parent = outline_parents[level - 1] if level > 0 else None
                
                # 添加大纲项
                outline_item = writer.add_outline_item(title, relative_page, parent=parent)
                
                # 更新当前层级的父大纲
                outline_parents[level] = outline_item
                
                # 清除更高层级的父大纲引用（因为可能是新的分支）
                for l in list(outline_parents.keys()):
                    if l > level:
                        del outline_parents[l]
                
                # 更新上一个大纲项的层级
                last_level = level
    
    @staticmethod
    def split(input_path, output_dir, split_mode="single", page_ranges=None, average_parts=None, progress_callback=None):
        """
        Split PDF file.
        split_mode: 
            - "single" (extract all pages as separate files)
            - "range" (extract specific ranges, each range as separate file)
            - "average" (split into N equal parts)
            - "outline" (split by outline items, each outline item as a separate file)
        page_ranges: string like "1-5, 8, 10-12" (1-based index)
        average_parts: number of parts to split into (for "average" mode)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # 使用pypdf打开PDF文件
        reader = PdfReader(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        total_pages = len(reader.pages)

        # 提取原始PDF的大纲信息，适配PdfMerger.merge方法添加的书签
        original_outlines = PdfSplitter._get_outlines(reader)

        if split_mode == "single":
            for i in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                
                # 添加大纲
                PdfSplitter._add_outlines(writer, original_outlines, i, i+1)
                
                # 保存文件
                output_filename = f"[{i+1}]{base_name}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                # 更新进度
                if progress_callback:
                    progress = int(((i + 1) / total_pages) * 100)
                    progress_callback(progress)
                    
        elif split_mode == "range" and page_ranges:
            # 解析页码范围
            parts = [p.strip() for p in page_ranges.split(',')]
            total_parts = len(parts)
            
            # 验证所有页码是否在有效范围内
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if start < 1 or end < 1:
                        raise ValueError(f"页码必须大于0，输入的范围 '{part}' 无效")
                    if start > total_pages or end > total_pages:
                        raise ValueError(f"页码超出范围：PDF只有{total_pages}页，输入的范围 '{part}' 无效")
                    if start > end:
                        raise ValueError(f"起始页码不能大于结束页码，输入的范围 '{part}' 无效")
                else:
                    page_num = int(part)
                    if page_num < 1:
                        raise ValueError(f"页码必须大于0，输入的页码 '{part}' 无效")
                    if page_num > total_pages:
                        raise ValueError(f"页码超出范围：PDF只有{total_pages}页，输入的页码 '{page_num}' 无效")
            
            for part_index, part in enumerate(parts):
                # 解析单个页码范围
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    # 转换为0-based索引
                    start_idx = start - 1
                    end_idx = end
                else:
                    # 单个页码
                    start_idx = int(part) - 1
                    end_idx = start_idx + 1
                
                writer = PdfWriter()
                
                # 添加指定范围的页面
                for i in range(start_idx, end_idx):
                    if 0 <= i < total_pages:
                        writer.add_page(reader.pages[i])
                
                # 添加大纲
                PdfSplitter._add_outlines(writer, original_outlines, start_idx, end_idx)
                
                # 保存文件
                output_filename = f"[{part}]{base_name}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                # 更新进度
                if progress_callback:
                    progress = int(((part_index + 1) / total_parts) * 100)
                    progress_callback(progress)
                    
        elif split_mode == "average" and average_parts:
            # 平均分割逻辑（按用户规则：前n-1份取最接近的整百数，最后一份取剩余页数）
            if average_parts <= 0:
                raise ValueError("Number of parts must be positive")
            
            # 计算每份的页数
            average = total_pages / average_parts
            page_per_part = round(average / 100) * 100
            
            start_page = 0
            for part_index in range(average_parts):
                # 最后一份取剩余所有页数
                if part_index == average_parts - 1:
                    end_page = total_pages
                else:
                    end_page = start_page + page_per_part
                    end_page = min(end_page, total_pages)
                
                # 跳过空的部分
                if start_page >= end_page:
                    continue
                
                writer = PdfWriter()
                
                # 添加指定范围的页面
                for i in range(start_page, end_page):
                    writer.add_page(reader.pages[i])
                
                # 添加大纲
                PdfSplitter._add_outlines(writer, original_outlines, start_page, end_page)
                
                # 生成文件名
                range_str = f"{start_page+1}-{end_page}"
                output_filename = f"[{range_str}]{base_name}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存文件
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                # 更新进度
                if progress_callback:
                    progress = int(((part_index + 1) / average_parts) * 100)
                    progress_callback(progress)
                
                # 更新起始页码
                start_page = end_page
                
        elif split_mode == "outline":
            # 按大纲拆分逻辑
            if not original_outlines:
                raise ValueError("No outlines found in the PDF file")
            
            # 按页码排序大纲项
            sorted_outlines = sorted(original_outlines, key=lambda x: x[1])
            total_outlines = len(sorted_outlines)
            
            for i, (title, start_page, _) in enumerate(sorted_outlines):
                # 确定当前大纲项的结束页码
                if i < total_outlines - 1:
                    # 下一个大纲项的起始页码作为当前大纲项的结束页码
                    end_page = sorted_outlines[i + 1][1]
                else:
                    # 最后一个大纲项，结束页码为总页数
                    end_page = total_pages
                
                writer = PdfWriter()
                
                # 添加指定范围的页面
                for j in range(start_page, end_page):
                    writer.add_page(reader.pages[j])
                
                # 添加大纲
                PdfSplitter._add_outlines(writer, original_outlines, start_page, end_page)
                
                # 生成文件名
                # 清理文件名，移除无效字符
                safe_title = title
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    safe_title = safe_title.replace(char, '_')
                output_filename = f"[{i+1}]{safe_title}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存文件
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                # 更新进度
                if progress_callback:
                    progress = int(((i + 1) / total_outlines) * 100)
                    progress_callback(progress)
                    
        return True
