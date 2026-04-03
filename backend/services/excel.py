"""
Excel 处理服务
支持信源 Excel 导入导出，支持三个板块的信源文件管理
"""
import pandas as pd
from typing import List, Dict, Any, Optional
import os


class ExcelService:
    """Excel 处理服务类"""

    SUPPORTED_BOARDS = ["时事", "财经", "科技"]

    def __init__(self):
        self._supported_boards = self.SUPPORTED_BOARDS.copy()


    def import_sources(self, file_path: str) -> Dict[str, Any]:
        """从 Excel 文件导入信源"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "data": [], "error": "文件不存在"}
            df = pd.read_excel(file_path)
            df = self._standardize_columns(df)
            sources = []
            for _, row in df.iterrows():
                source = {"name": str(row.get("信源名称", "")), "url": str(row.get("信源 URL", "")), "category": str(row.get("分类", "")), "weight": int(row.get("权重", 1)) if pd.notna(row.get("权重")) else 1, "board": str(row.get("板块", ""))}
                if source["name"] and source["url"]: sources.append(source)
            return {"success": True, "data": sources, "error": ""}
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}


    def import_sources_from_binary(self, file_content: bytes) -> Dict[str, Any]:
        """从二进制内容导入信源"""
        try:
            from io import BytesIO
            df = pd.read_excel(BytesIO(file_content))
            df = self._standardize_columns(df)
            sources = []
            for _, row in df.iterrows():
                name = str(row.get("信源名称", "")).strip()
                url = str(row.get("信源 URL", "")).strip()
                category = str(row.get("分类", "")).strip()
                board = str(row.get("板块", "")).strip()
                raw_weight = row.get("权重")
                weight = int(raw_weight) if pd.notna(raw_weight) and str(raw_weight).strip() not in ("", "nan") else 5
                # 过滤空值和 NaN 占位符
                if name and name != "nan" and url and url != "nan":
                    sources.append({
                        "name": name,
                        "url": url,
                        "category": category if category != "nan" else "",
                        "weight": weight,
                        "board": board if board != "nan" else "",
                    })
            return {"success": True, "data": sources, "error": ""}
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}


    def export_sources(self, sources, output_path: str, board=None) -> Dict[str, Any]:
        """导出信源到 Excel 文件"""
        try:
            if board: sources = [s for s in sources if s.get("board") == board]
            if not sources: return {"success": False, "path": "", "error": "没有可导出的数据"}
            data = [{"信源名称": s.get("name",""), "信源 URL": s.get("url",""), "分类": s.get("category",""), "权重": s.get("weight",1), "板块": s.get("board","")} for s in sources]
            df = pd.DataFrame(data)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)
            df.to_excel(output_path, index=False, sheet_name="信源列表")
            return {"success": True, "path": output_path, "error": ""}
        except Exception as e:
            return {"success": False, "path": "", "error": str(e)}


    def export_sources_to_bytes(self, sources, board=None) -> Dict[str, Any]:
        """导出信源为二进制 Excel 内容"""
        try:
            from io import BytesIO
            if board: sources = [s for s in sources if s.get("board") == board]
            if not sources: return {"success": False, "content": b"", "error": "没有可导出的数据"}
            data = [{"信源名称": s.get("name",""), "信源 URL": s.get("url",""), "分类": s.get("category",""), "权重": s.get("weight",1), "板块": s.get("board","")} for s in sources]
            df = pd.DataFrame(data)
            buffer = BytesIO()
            df.to_excel(buffer, index=False, sheet_name="信源列表")
            buffer.seek(0)
            return {"success": True, "content": buffer.getvalue(), "error": ""}
        except Exception as e:
            return {"success": False, "content": b"", "error": str(e)}


    def export_multi_board_sources(self, sources, output_path: str) -> Dict[str, Any]:
        """导出多板块信源到 Excel 文件"""
        try:
            if not sources: return {"success": False, "path": "", "error": "没有可导出的数据"}
            board_sources = {}
            for source in sources:
                brd = source.get("board", "未分类")
                if brd not in board_sources: board_sources[brd] = []
                board_sources[brd].append(source)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for brd, board_data in board_sources.items():
                    data = [{"信源名称": s.get("name",""), "信源 URL": s.get("url",""), "分类": s.get("category",""), "权重": s.get("weight",1), "板块": s.get("board","")} for s in board_data]
                    df = pd.DataFrame(data)
                    df.to_excel(writer, index=False, sheet_name=brd[:31])
            return {"success": True, "path": output_path, "error": ""}
        except Exception as e:
            return {"success": False, "path": "", "error": str(e)}


    def _standardize_columns(self, df):
        """标准化列名，兼容多种 Excel 格式"""
        # 统一映射到内部标准列名
        column_mapping = {
            # 名称字段
            "网站名称": "信源名称", "source_name": "信源名称", "name": "信源名称",
            # URL 字段
            "URL": "信源 URL", "官方地址": "信源 URL", "source_url": "信源 URL", "url": "信源 URL",
            # 分类字段
            "信息分类": "分类", "category": "分类",
            # 权重字段
            "weight": "权重",
            # 板块字段
            "board": "板块",
        }
        df = df.rename(columns=column_mapping)
        # 确保必要列存在
        for col in ["信源名称", "信源 URL", "分类", "权重", "板块"]:
            if col not in df.columns:
                df[col] = ""
        return df


    def validate_source_file(self, file_path: str) -> Dict[str, Any]:
        """验证信源 Excel 文件格式"""
        try:
            if not os.path.exists(file_path): return {"valid": False, "error": "文件不存在"}
            df = pd.read_excel(file_path)
            df = self._standardize_columns(df)
            missing_cols = []
            if "信源名称" not in df.columns: missing_cols.append("信源名称")
            if "信源 URL" not in df.columns: missing_cols.append("信源 URL")
            if missing_cols: return {"valid": False, "error": "缺少必要列：" + str(missing_cols)}
            if len(df) == 0: return {"valid": False, "error": "文件为空"}
            if "板块" in df.columns:
                boards = set(df["板块"].dropna().unique())
                invalid_boards = boards - set(self._supported_boards) - {""}
                if invalid_boards: return {"valid": True, "warning": "存在未定义的板块：" + str(invalid_boards)}
            return {"valid": True, "row_count": len(df)}
        except Exception as e:
            return {"valid": False, "error": str(e)}


    def get_template(self, output_path: str) -> Dict[str, Any]:
        """生成信源 Excel 模板文件"""
        try:
            data = {"信源名称": ["示例信源 1", "示例信源 2"], "信源 URL": ["https://example.com/1", "https://example.com/2"], "分类": ["时事", "财经"], "权重": [5, 3], "板块": ["时事", "财经"]}
            df = pd.DataFrame(data)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)
            df.to_excel(output_path, index=False, sheet_name="信源模板")
            return {"success": True, "path": output_path, "error": ""}
        except Exception as e:
            return {"success": False, "path": "", "error": str(e)}


    def add_supported_board(self, board: str) -> None:
        """添加支持的板块"""
        if board not in self._supported_boards:
            self._supported_boards.append(board)


    def get_supported_boards(self) -> List[str]:
        """获取支持的板块列表"""
        return self._supported_boards.copy()
