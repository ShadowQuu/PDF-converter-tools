"""
交互式PDF查看器组件 - 支持查看、选择、高亮、批注等功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QToolBar, QPushButton, QSpinBox,
    QColorDialog, QInputDialog, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPixmap, QImage, QPainter, QColor, QPen, 
    QBrush, QMouseEvent, QKeyEvent, QAction
)
import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)


class PDFPageWidget(QWidget):
    """PDF页面显示组件"""
    
    # 信号
    text_selected = pyqtSignal(str)  # 文本被选中
    annotation_added = pyqtSignal(dict)  # 注释被添加
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page = None
        self.pixmap = None
        self.scale = 1.5  # 默认缩放比例
        self.annotations = []  # 注释列表
        self.current_tool = "select"  # 当前工具: select, highlight, underline, note
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        self.setMinimumSize(600, 800)
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def set_page(self, page):
        """设置PDF页面"""
        self.page = page
        self.render_page()
    
    def render_page(self):
        """渲染页面"""
        if not self.page:
            return
        
        # 使用PyMuPDF渲染页面
        mat = fitz.Matrix(self.scale, self.scale)
        pix = self.page.get_pixmap(matrix=mat)
        
        # 转换为QPixmap
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(img)
        
        # 调整窗口大小
        self.setFixedSize(self.pixmap.size())
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        # 绘制页面
        if self.pixmap:
            painter.drawPixmap(0, 0, self.pixmap)
        
        # 绘制注释
        for ann in self.annotations:
            self.draw_annotation(painter, ann)
        
        # 绘制选择区域
        if self.is_selecting and self.selection_start and self.selection_end:
            rect = QRectF(self.selection_start, self.selection_end).normalized()
            painter.fillRect(rect, QColor(0, 120, 255, 50))
            painter.setPen(QPen(QColor(0, 120, 255), 1))
            painter.drawRect(rect)
    
    def draw_annotation(self, painter, ann):
        """绘制注释"""
        if ann['type'] == 'highlight':
            painter.fillRect(ann['rect'], QColor(255, 255, 0, 100))
        elif ann['type'] == 'underline':
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            y = ann['rect'].bottom()
            painter.drawLine(int(ann['rect'].left()), int(y), int(ann['rect'].right()), int(y))
        elif ann['type'] == 'note':
            painter.setBrush(QBrush(QColor(255, 255, 0)))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(ann['pos'], 10, 10)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if not self.page:
            return
        
        pos = event.pos()
        
        if self.current_tool == "select":
            self.selection_start = QPointF(pos)
            self.selection_end = QPointF(pos)
            self.is_selecting = True
        elif self.current_tool in ['highlight', 'underline']:
            self.selection_start = QPointF(pos)
            self.selection_end = QPointF(pos)
            self.is_selecting = True
        elif self.current_tool == 'note':
            # 添加批注
            self.add_note_annotation(pos)
        
        self.update()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.is_selecting:
            self.selection_end = QPointF(event.pos())
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if not self.is_selecting:
            return
        
        self.is_selecting = False
        
        if self.current_tool == "select":
            # 提取选中的文本
            self.extract_selected_text()
        elif self.current_tool == 'highlight':
            self.add_highlight_annotation()
        elif self.current_tool == 'underline':
            self.add_underline_annotation()
        
        self.selection_start = None
        self.selection_end = None
        self.update()
    
    def extract_selected_text(self):
        """提取选中的文本"""
        if not self.selection_start or not self.selection_end:
            return
        
        # 将屏幕坐标转换为PDF坐标
        rect = QRectF(self.selection_start, self.selection_end).normalized()
        pdf_rect = fitz.Rect(
            rect.left() / self.scale,
            rect.top() / self.scale,
            rect.right() / self.scale,
            rect.bottom() / self.scale
        )
        
        # 提取文本
        text = self.page.get_text("text", clip=pdf_rect)
        if text.strip():
            self.text_selected.emit(text.strip())
    
    def add_highlight_annotation(self):
        """添加高亮注释"""
        if not self.selection_start or not self.selection_end:
            return
        
        rect = QRectF(self.selection_start, self.selection_end).normalized()
        
        annotation = {
            'type': 'highlight',
            'rect': rect,
            'page': self.page.number
        }
        self.annotations.append(annotation)
        self.annotation_added.emit(annotation)
    
    def add_underline_annotation(self):
        """添加下划线注释"""
        if not self.selection_start or not self.selection_end:
            return
        
        rect = QRectF(self.selection_start, self.selection_end).normalized()
        
        annotation = {
            'type': 'underline',
            'rect': rect,
            'page': self.page.number
        }
        self.annotations.append(annotation)
        self.annotation_added.emit(annotation)
    
    def add_note_annotation(self, pos):
        """添加文本批注"""
        text, ok = QInputDialog.getText(self, "添加批注", "请输入批注内容:")
        if ok and text:
            annotation = {
                'type': 'note',
                'pos': pos,
                'text': text,
                'page': self.page.number
            }
            self.annotations.append(annotation)
            self.annotation_added.emit(annotation)
    
    def set_tool(self, tool_name):
        """设置当前工具"""
        self.current_tool = tool_name
        
        if tool_name == "select":
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif tool_name in ['highlight', 'underline']:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool_name == 'note':
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def zoom_in(self):
        """放大"""
        self.scale *= 1.2
        self.render_page()
    
    def zoom_out(self):
        """缩小"""
        self.scale /= 1.2
        self.render_page()
    
    def clear_annotations(self):
        """清除所有注释"""
        self.annotations.clear()
        self.update()


class PDFViewerWidget(QWidget):
    """PDF查看器主组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.document = None
        self.current_page_num = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar = QToolBar()
        
        # 文件操作
        self.btn_open = QPushButton("打开PDF")
        self.btn_open.clicked.connect(self.open_pdf)
        toolbar.addWidget(self.btn_open)
        
        toolbar.addSeparator()
        
        # 页面导航
        toolbar.addWidget(QLabel("页面:"))
        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setValue(1)
        self.spin_page.valueChanged.connect(self.go_to_page)
        toolbar.addWidget(self.spin_page)
        
        self.lbl_total_pages = QLabel("/ 0")
        toolbar.addWidget(self.lbl_total_pages)
        
        toolbar.addSeparator()
        
        # 缩放控制
        self.btn_zoom_in = QPushButton("放大")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.btn_zoom_in)
        
        self.btn_zoom_out = QPushButton("缩小")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.btn_zoom_out)
        
        toolbar.addSeparator()
        
        # 工具选择
        self.btn_select = QPushButton("选择文本")
        self.btn_select.setCheckable(True)
        self.btn_select.setChecked(True)
        self.btn_select.clicked.connect(lambda: self.set_tool("select"))
        toolbar.addWidget(self.btn_select)
        
        self.btn_highlight = QPushButton("高亮")
        self.btn_highlight.setCheckable(True)
        self.btn_highlight.clicked.connect(lambda: self.set_tool("highlight"))
        toolbar.addWidget(self.btn_highlight)
        
        self.btn_underline = QPushButton("下划线")
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(lambda: self.set_tool("underline"))
        toolbar.addWidget(self.btn_underline)
        
        self.btn_note = QPushButton("批注")
        self.btn_note.setCheckable(True)
        self.btn_note.clicked.connect(lambda: self.set_tool("note"))
        toolbar.addWidget(self.btn_note)
        
        layout.addWidget(toolbar)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # PDF页面显示
        self.page_widget = PDFPageWidget()
        self.page_widget.text_selected.connect(self.on_text_selected)
        scroll.setWidget(self.page_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def open_pdf(self, file_path=None):
        """打开PDF文件"""
        if not file_path:
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, "打开PDF文件", "", "PDF文件 (*.pdf)"
            )
        
        if file_path:
            try:
                self.document = fitz.open(file_path)
                self.current_page_num = 0
                self.spin_page.setMaximum(len(self.document))
                self.lbl_total_pages.setText(f"/ {len(self.document)}")
                self.load_page(0)
                logger.info(f"打开PDF文件: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开PDF文件: {str(e)}")
    
    def load_page(self, page_num):
        """加载指定页面"""
        if not self.document or page_num < 0 or page_num >= len(self.document):
            return
        
        self.current_page_num = page_num
        page = self.document[page_num]
        self.page_widget.set_page(page)
        self.spin_page.setValue(page_num + 1)
    
    def go_to_page(self, page_num):
        """跳转到指定页面"""
        if self.document:
            self.load_page(page_num - 1)
    
    def zoom_in(self):
        """放大"""
        self.page_widget.zoom_in()
    
    def zoom_out(self):
        """缩小"""
        self.page_widget.zoom_out()
    
    def set_tool(self, tool_name):
        """设置当前工具"""
        # 取消所有按钮的选中状态
        self.btn_select.setChecked(False)
        self.btn_highlight.setChecked(False)
        self.btn_underline.setChecked(False)
        self.btn_note.setChecked(False)
        
        # 设置当前按钮为选中状态
        if tool_name == "select":
            self.btn_select.setChecked(True)
        elif tool_name == "highlight":
            self.btn_highlight.setChecked(True)
        elif tool_name == "underline":
            self.btn_underline.setChecked(True)
        elif tool_name == "note":
            self.btn_note.setChecked(True)
        
        self.page_widget.set_tool(tool_name)
    
    def on_text_selected(self, text):
        """文本被选中时的处理"""
        # 复制到剪贴板
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # 显示提示
        QMessageBox.information(self, "文本已复制", f"已复制到剪贴板:\n{text[:100]}...")
    
    def save_pdf(self, output_path):
        """保存PDF（带注释）"""
        if not self.document:
            return
        
        try:
            # 这里可以实现将注释保存到PDF的功能
            self.document.save(output_path)
            QMessageBox.information(self, "成功", "PDF已保存！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
