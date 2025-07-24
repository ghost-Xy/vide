import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QListWidgetItem,
                             QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QGroupBox, QComboBox, QCheckBox, QProgressBar,
                             QStackedWidget, QTabWidget, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QImage
import cv2
import numpy as np

class AutoVideoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量自动剪辑工具")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.png"))
        
        # 初始化UI
        self.initUI()
        
        # 初始化变量
        self.current_file_index = -1
        self.video_files = []
        self.preview_image = None
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QGroupBox {
                border: 1px solid #34495e;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QListWidget {
                background-color: #34495e;
                border: none;
                border-radius: 5px;
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 4px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 5px;
                text-align: center;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
    
    def initUI(self):
        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 左侧面板 - 文件管理
        left_panel = QGroupBox("视频文件管理")
        left_panel.setMinimumWidth(300)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(400)
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        left_layout.addWidget(self.file_list)
        
        # 文件操作按钮
        btn_layout = QHBoxLayout()
        add_files_btn = QPushButton("添加文件")
        add_files_btn.setIcon(QIcon("icons/add.png"))
        add_files_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_files_btn)
        
        add_folder_btn = QPushButton("添加文件夹")
        add_folder_btn.setIcon(QIcon("icons/folder.png"))
        add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_folder_btn)
        
        remove_btn = QPushButton("移除")
        remove_btn.setIcon(QIcon("icons/remove.png"))
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.setIcon(QIcon("icons/clear.png"))
        clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(clear_btn)
        
        left_layout.addLayout(btn_layout)
        
        # 输出路径
        output_layout = QHBoxLayout()
        output_label = QLabel("输出路径:")
        output_layout.addWidget(output_label)
        
        self.output_path_label = QLabel()
        self.output_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        output_layout.addWidget(self.output_path_label, 1)
        
        browse_btn = QPushButton("浏览")
        browse_btn.setIcon(QIcon("icons/browse.png"))
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_btn)
        left_layout.addLayout(output_layout)
        
        # 预览图像
        self.preview_label = QLabel("视频预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("background-color: #34495e; border-radius: 5px;")
        left_layout.addWidget(self.preview_label)
        
        # 中间面板 - 预览和处理
        middle_panel = QGroupBox("预览和处理")
        middle_layout = QVBoxLayout()
        middle_panel.setLayout(middle_layout)
        
        # 预览信息
        info_layout = QHBoxLayout()
        self.file_info_label = QLabel("选择视频文件开始预览")
        self.file_info_label.setWordWrap(True)
        info_layout.addWidget(self.file_info_label)
        
        # 处理控制按钮
        process_layout = QHBoxLayout()
        self.process_current_btn = QPushButton("处理当前文件")
        self.process_current_btn.setIcon(QIcon("icons/process.png"))
        self.process_current_btn.setEnabled(False)
        process_layout.addWidget(self.process_current_btn)
        
        self.process_all_btn = QPushButton("批量处理所有")
        self.process_all_btn.setIcon(QIcon("icons/process_all.png"))
        self.process_all_btn.setEnabled(False)
        process_layout.addWidget(self.process_all_btn)
        info_layout.addLayout(process_layout)
        middle_layout.addLayout(info_layout)
        
        # 处理进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        middle_layout.addWidget(self.progress_bar)
        
        # 右侧面板 - 处理设置
        right_panel = QTabWidget()
        right_panel.setMinimumWidth(400)
        
        # 去重方案标签页
        dedupe_tab = QWidget()
        dedupe_layout = QVBoxLayout()
        dedupe_tab.setLayout(dedupe_layout)
        
        dedupe_layout.addWidget(QLabel("<b>去重方案</b>"))
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设方案:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["初级去重", "中级去重", "高级去重", "自定义"])
        preset_layout.addWidget(self.preset_combo)
        dedupe_layout.addLayout(preset_layout)
        
        # 处理选项组
        options_group = QGroupBox("处理选项")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # 基础处理选项
        self.crop_check = QCheckBox("裁剪")
        self.crop_check.setChecked(True)
        options_layout.addWidget(self.crop_check)
        
        self.filter_check = QCheckBox("滤镜")
        self.filter_check.setChecked(True)
        options_layout.addWidget(self.filter_check)
        
        self.mirror_check = QCheckBox("镜像")
        options_layout.addWidget(self.mirror_check)
        
        self.speed_check = QCheckBox("变速")
        self.speed_check.setChecked(True)
        options_layout.addWidget(self.speed_check)
        
        # 高级处理选项
        adv_group = QGroupBox("高级选项")
        adv_layout = QVBoxLayout()
        adv_group.setLayout(adv_layout)
        
        self.shake_check = QCheckBox("抖动效果")
        adv_layout.addWidget(self.shake_check)
        
        self.framedrop_check = QCheckBox("抽帧快剪")
        adv_layout.addWidget(self.framedrop_check)
        
        self.combo_label = QLabel("合成方式:")
        adv_layout.addWidget(self.combo_label)
        
        self.combo_combo = QComboBox()
        self.combo_combo.addItems(["顺序合成", "随机合成", "混剪合成", "场景重组"])
        adv_layout.addWidget(self.combo_combo)
        
        options_layout.addWidget(adv_group)
        
        dedupe_layout.addWidget(options_group)
        
        # 参数设置
        params_group = QGroupBox("参数设置")
        params_layout = QVBoxLayout()
        params_group.setLayout(params_layout)
        
        crop_layout = QHBoxLayout()
        crop_layout.addWidget(QLabel("裁剪比例:"))
        self.crop_spin = QSpinBox()
        self.crop_spin.setRange(1, 30)
        self.crop_spin.setValue(15)
        self.crop_spin.setSuffix("%")
        crop_layout.addWidget(self.crop_spin)
        params_layout.addLayout(crop_layout)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("变速范围:"))
        self.speed_min_spin = QDoubleSpinBox()
        self.speed_min_spin.setRange(0.5, 1.5)
        self.speed_min_spin.setValue(0.9)
        self.speed_min_spin.setSingleStep(0.1)
        speed_layout.addWidget(self.speed_min_spin)
        
        speed_layout.addWidget(QLabel("到"))
        self.speed_max_spin = QDoubleSpinBox()
        self.speed_max_spin.setRange(0.5, 1.5)
        self.speed_max_spin.setValue(1.1)
        self.speed_max_spin.setSingleStep(0.1)
        speed_layout.addWidget(self.speed_max_spin)
        params_layout.addLayout(speed_layout)
        
        dedupe_layout.addWidget(params_group)
        
        # 混剪方案标签页
        mix_tab = QWidget()
        mix_layout = QVBoxLayout()
        mix_tab.setLayout(mix_layout)
        
        mix_layout.addWidget(QLabel("<b>混剪合成设置</b>"))
        
        # 保存模板按钮
        save_template_btn = QPushButton("保存当前为模板")
        save_template_btn.setIcon(QIcon("icons/save.png"))
        mix_layout.addWidget(save_template_btn)
        
        # 添加到标签页
        right_panel.addTab(dedupe_tab, "去重设置")
        right_panel.addTab(mix_tab, "混剪设置")
        
        # 添加到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(middle_panel)
        main_layout.addWidget(right_panel)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv)"
        )
        if files:
            self.video_files.extend(files)
            self.update_file_list()
    
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择视频文件夹")
        if folder:
            valid_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv')
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(valid_extensions):
                        self.video_files.append(os.path.join(root, file))
            self.update_file_list()
    
    def browse_output(self):
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if output_dir:
            self.output_path_label.setText(output_dir)
            self.process_current_btn.setEnabled(True)
            self.process_all_btn.setEnabled(bool(self.video_files))
    
    def remove_selected(self):
        selected_items = self.file_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.file_list.row(item)
                del self.video_files[row]
            self.update_file_list()
    
    def clear_files(self):
        self.video_files = []
        self.update_file_list()
    
    def update_file_list(self):
        self.file_list.clear()
        for file_path in self.video_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)
            self.file_list.addItem(item)
        
        self.process_all_btn.setEnabled(bool(self.video_files) and self.output_path_label.text())
    
    def on_file_selected(self):
        selected = self.file_list.selectedItems()
        if selected:
            self.current_file_index = self.file_list.row(selected[0])
            self.load_preview()
    
    def load_preview(self):
        if not self.video_files or self.current_file_index < 0:
            return
        
        file_path = self.video_files[self.current_file_index]
        
        # 获取文件信息
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return
        
        # 读取第一帧
        ret, frame = cap.read()
        if ret:
            # 转换为Qt格式
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # 调整预览大小
            max_width = self.preview_label.width() - 20
            max_height = 300
            if pixmap.width() > max_width:
                pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
            if pixmap.height() > max_height:
                pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
            
            self.preview_label.setPixmap(pixmap)
            cap.release()
            
            # 显示文件信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
            
            info = f"""
<b>{os.path.basename(file_path)}</b><br>
大小: {width}×{height} @ {fps:.1f}fps<br>
时长: {duration:.1f}秒<br>
路径: {os.path.dirname(file_path)}
"""
            self.file_info_label.setText(info)
    
    def resizeEvent(self, event):
        if self.current_file_index >= 0:
            self.load_preview()
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoVideoEditor()
    window.show()
    sys.exit(app.exec_())