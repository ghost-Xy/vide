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
from video_processor import VideoProcessor
from template_manager import TemplateManager
import utils

class AutoVideoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量自动剪辑工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口图标
        icon_path = os.path.join("icons", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 初始化UI
        self.initUI()
        
        # 初始化变量
        self.current_file_index = -1
        self.video_files = []
        self.preview_image = None
        self.video_processor = VideoProcessor()
        self.template_manager = TemplateManager()
        self.output_dir = os.path.join(os.getcwd(), "output")
        
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
        self.add_files_btn = QPushButton("添加文件")
        self.add_files_btn.setIcon(QIcon("icons/add.png" if os.path.exists("icons/add.png") else ""))
        self.add_files_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_files_btn)
        
        self.add_folder_btn = QPushButton("添加文件夹")
        self.add_folder_btn.setIcon(QIcon("icons/folder.png" if os.path.exists("icons/folder.png") else ""))
        self.add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(self.add_folder_btn)
        
        self.remove_btn = QPushButton("移除")
        self.remove_btn.setIcon(QIcon("icons/remove.png" if os.path.exists("icons/remove.png") else ""))
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setIcon(QIcon("icons/clear.png" if os.path.exists("icons/clear.png") else ""))
        self.clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.clear_btn)
        
        left_layout.addLayout(btn_layout)
        
        # 输出路径
        output_layout = QHBoxLayout()
        output_label = QLabel("输出路径:")
        output_layout.addWidget(output_label)
        
        self.output_path_label = QLabel(self.output_dir)
        self.output_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        output_layout.addWidget(self.output_path_label, 1)
        
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setIcon(QIcon("icons/browse.png" if os.path.exists("icons/browse.png") else ""))
        self.browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.browse_btn)
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
        self.process_current_btn.setIcon(QIcon("icons/process.png" if os.path.exists("icons/process.png") else ""))
        self.process_current_btn.setEnabled(False)
        self.process_current_btn.clicked.connect(self.process_current)
        process_layout.addWidget(self.process_current_btn)
        
        self.process_all_btn = QPushButton("批量处理所有")
        self.process_all_btn.setIcon(QIcon("icons/process_all.png" if os.path.exists("icons/process_all.png") else ""))
        self.process_all_btn.setEnabled(False)
        self.process_all_btn.clicked.connect(self.process_all)
        process_layout.addWidget(self.process_all_btn)
        info_layout.addLayout(process_layout)
        middle_layout.addLayout(info_layout)
        
        # 处理进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        middle_layout.addWidget(self.progress_bar)
        
        # 右侧面板 - 处理设置
        self.right_panel = QTabWidget()
        self.right_panel.setMinimumWidth(400)
        
        # 去重方案标签页
        dedupe_tab = QWidget()
        dedupe_layout = QVBoxLayout()
        dedupe_tab.setLayout(dedupe_layout)
        
        dedupe_layout.addWidget(QLabel("<b>去重方案</b>"))
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设方案:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["初级去重", "中级去重", "高级去重", "自定义"])
        self.preset_combo.currentIndexChanged.connect(self.load_preset)
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
        
        # 混剪选项
        mix_options_group = QGroupBox("混剪选项")
        mix_options_layout = QVBoxLayout()
        mix_options_group.setLayout(mix_options_layout)
        
        self.clip_duration_label = QLabel("单段最大时长 (秒):")
        mix_options_layout.addWidget(self.clip_duration_label)
        
        self.clip_duration_spin = QSpinBox()
        self.clip_duration_spin.setRange(1, 60)
        self.clip_duration_spin.setValue(5)
        mix_options_layout.addWidget(self.clip_duration_spin)
        
        self.min_clips_label = QLabel("每个视频最少片段数:")
        mix_options_layout.addWidget(self.min_clips_label)
        
        self.min_clips_spin = QSpinBox()
        self.min_clips_spin.setRange(1, 20)
        self.min_clips_spin.setValue(3)
        mix_options_layout.addWidget(self.min_clips_spin)
        
        mix_layout.addWidget(mix_options_group)
        
        # 保存模板按钮
        self.save_template_btn = QPushButton("保存当前为模板")
        self.save_template_btn.setIcon(QIcon("icons/save.png" if os.path.exists("icons/save.png") else ""))
        self.save_template_btn.clicked.connect(self.save_template)
        mix_layout.addWidget(self.save_template_btn)
        
        # 添加到标签页
        self.right_panel.addTab(dedupe_tab, "去重设置")
        self.right_panel.addTab(mix_tab, "混剪设置")
        
        # 添加到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(middle_panel)
        main_layout.addWidget(self.right_panel)
    
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
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_dir)
        if output_dir:
            self.output_dir = output_dir
            self.output_path_label.setText(self.output_dir)
            self.update_buttons_state()
    
    def remove_selected(self):
        selected_items = self.file_list.selectedItems()
        if selected_items:
            indices = [self.file_list.row(item) for item in selected_items]
            # 从后往前删除避免索引变化
            for index in sorted(indices, reverse=True):
                del self.video_files[index]
            self.update_file_list()
    
    def clear_files(self):
        self.video_files = []
        self.current_file_index = -1
        self.update_file_list()
    
    def update_file_list(self):
        self.file_list.clear()
        for file_path in self.video_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)
            self.file_list.addItem(item)
        
        self.update_buttons_state()
    
    def update_buttons_state(self):
        has_files = len(self.video_files) > 0
        has_output_dir = self.output_dir and os.path.isdir(self.output_dir)
        
        self.process_current_btn.setEnabled(has_files and has_output_dir and self.current_file_index >= 0)
        self.process_all_btn.setEnabled(has_files and has_output_dir)
    
    def on_file_selected(self):
        selected = self.file_list.selectedItems()
        if selected:
            self.current_file_index = self.file_list.row(selected[0])
            self.load_preview()
            self.update_buttons_state()
    
    def load_preview(self):
        if not self.video_files or self.current_file_index < 0:
            self.preview_label.clear()
            self.file_info_label.setText("选择视频文件开始预览")
            return
        
        file_path = self.video_files[self.current_file_index]
        
        # 获取文件信息
        info = utils.get_video_info(file_path)
        if not info:
            self.preview_label.setText("无法读取视频文件")
            self.file_info_label.setText(f"无法读取文件: {file_path}")
            return
        
        # 显示文件信息
        info_text = f"""
<b>{os.path.basename(file_path)}</b><br>
分辨率: {info['width']}×{info['height']} @ {info['fps']:.1f}fps<br>
时长: {utils.format_duration(info['duration'])}<br>
路径: {os.path.dirname(file_path)}
"""
        self.file_info_label.setText(info_text)
        
        # 获取并显示预览帧
        frame = utils.get_frame_preview(file_path)
        if frame is not None:
            # 转换为Qt格式
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # 调整预览大小
            max_width = self.preview_label.width() - 20
            max_height = 300
            if pixmap.width() > max_width:
                pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
            if pixmap.height() > max_height:
                pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
            
            self.preview_label.setPixmap(pixmap)
    
    def resizeEvent(self, event):
        if self.current_file_index >= 0:
            self.load_preview()
        super().resizeEvent(event)
    
    def load_preset(self):
        """根据选择的预设方案设置处理选项"""
        preset = self.preset_combo.currentText()
        
        # 重置所有选项
        self.crop_check.setChecked(True)
        self.filter_check.setChecked(True)
        self.mirror_check.setChecked(False)
        self.speed_check.setChecked(True)
        self.shake_check.setChecked(False)
        self.framedrop_check.setChecked(False)
        self.crop_spin.setValue(15)
        self.speed_min_spin.setValue(0.9)
        self.speed_max_spin.setValue(1.1)
        
        # 设置不同预设的选项
        if preset == "初级去重":
            # 基础选项保持不变
            pass
        elif preset == "中级去重":
            self.mirror_check.setChecked(True)
            self.crop_spin.setValue(20)
            self.speed_min_spin.setValue(0.8)
            self.speed_max_spin.setValue(1.2)
        elif preset == "高级去重":
            self.mirror_check.setChecked(True)
            self.shake_check.setChecked(True)
            self.framedrop_check.setChecked(True)
            self.crop_spin.setValue(25)
            self.speed_min_spin.setValue(0.7)
            self.speed_max_spin.setValue(1.3)
    
    def save_template(self):
        """保存当前设置为模板"""
        template_name, ok = QInputDialog.getText(
            self, "保存模板", "请输入模板名称:",
            QLineEdit.Normal, ""
        )
        
        if not ok or not template_name:
            return
        
        # 获取当前设置
        config = self.get_current_config()
        
        # 保存模板
        tm = TemplateManager()
        if tm.save_template(template_name, config):
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 保存成功!")
        else:
            QMessageBox.warning(self, "错误", "保存模板失败!")
    
    def get_current_config(self):
        """获取当前UI配置"""
        return {
            "preset": self.preset_combo.currentText(),
            "crop": self.crop_check.isChecked(),
            "crop_percent": self.crop_spin.value(),
            "filter": self.filter_check.isChecked(),
            "mirror": self.mirror_check.isChecked(),
            "speed": self.speed_check.isChecked(),
            "min_speed": self.speed_min_spin.value(),
            "max_speed": self.speed_max_spin.value(),
            "shake": self.shake_check.isChecked(),
            "framedrop": self.framedrop_check.isChecked(),
            "combo_method": self.combo_combo.currentText(),
            "clip_duration": self.clip_duration_spin.value(),
            "min_clips": self.min_clips_spin.value()
        }
    
    def process_current(self):
        """处理当前选中的视频"""
        if self.current_file_index < 0 or not self.video_files:
            return
        
        input_path = self.video_files[self.current_file_index]
        config = self.get_current_config()
        
        # 生成输出文件名
        output_path = utils.generate_output_filename(
            input_path, self.output_dir, 
            suffix=f"_{config['preset']}"
        )
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 异步处理视频
        self.worker = VideoProcessorThread(
            self.video_processor, 
            input_path, 
            output_path, 
            config,
            progress_callback=self.update_progress
        )
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()
    
    def process_all(self):
        """批量处理所有视频"""
        if not self.video_files:
            return
        
        config = self.get_current_config()
        total = len(self.video_files)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total * 100)
        self.progress_bar.setValue(0)
        
        self.current_batch = 0
        self.batch_results = []
        self.process_next()
    
    def process_next(self):
        """处理下一个视频"""
        if self.current_batch >= len(self.video_files):
            # 处理完成
            self.progress_bar.setVisible(False)
            success_count = sum(self.batch_results)
            QMessageBox.information(
                self, "处理完成", 
                f"批量处理完成!\n成功: {success_count}, 失败: {len(self.batch_results) - success_count}"
            )
            return
        
        input_path = self.video_files[self.current_batch]
        config = self.get_current_config()
        
        # 生成输出文件名
        output_path = utils.generate_output_filename(
            input_path, self.output_dir, 
            suffix=f"_{config['preset']}"
        )
        
        # 处理视频
        success = self.video_processor.process_video(
            input_path, 
            output_path, 
            config, 
            progress_callback=lambda p: self.update_progress(p, self.current_batch)
        )
        
        self.batch_results.append(success)
        self.current_batch += 1
        self.update_progress(100, self.current_batch)
        self.process_next()
    
    def update_progress(self, progress, batch_index=0):
        """更新进度条"""
        if batch_index >= 0:
            # 批量处理，计算总体进度
            total = len(self.video_files)
            batch_progress = int((batch_index * 100) + progress)
            overall_progress = min(batch_progress, total * 100)
            self.progress_bar.setValue(overall_progress)
        else:
            # 单文件处理
            self.progress_bar.setValue(progress)
    
    def on_process_finished(self, success):
        """单个视频处理完成回调"""
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "成功", "视频处理完成!")
        else:
            QMessageBox.warning(self, "错误", "视频处理失败!")


class VideoProcessorThread(QThread):
    finished = pyqtSignal(bool)
    
    def __init__(self, processor, input_path, output_path, config, progress_callback):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
        self.config = config
        self.progress_callback = progress_callback
    
    def run(self):
        try:
            success = self.processor.process_video(
                self.input_path,
                self.output_path,
                self.config,
                progress_callback=self.progress_callback
            )
            self.finished.emit(success)
        except Exception as e:
            print(f"处理失败: {str(e)}")
            self.finished.emit(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoVideoEditor()
    window.show()
    sys.exit(app.exec_())