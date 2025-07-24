import os
import cv2
import random
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, Callable
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VideoUtils")

def get_video_info(video_path: str) -> dict:
    """获取视频元信息"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}
        
        info = {
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            "codec": int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        cap.release()
        return info
    except Exception as e:
        logger.error(f"获取视频信息失败: {str(e)}")
        return {}

def resize_frame(frame, target_size: Tuple[int, int]) -> cv2.Mat:
    """调整帧尺寸保持宽高比"""
    h, w = frame.shape[:2]
    target_w, target_h = target_size
    
    # 计算缩放比例
    scale = min(target_w / w, target_h / h)
    new_size = (int(w * scale), int(h * scale))
    
    # 调整尺寸
    resized = cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)
    
    # 填充黑边
    delta_w = target_w - new_size[0]
    delta_h = target_h - new_size[1]
    top, bottom = delta_h//2, delta_h - (delta_h//2)
    left, right = delta_w//2, delta_w - (delta_w//2)
    
    return cv2.copyMakeBorder(
        resized, top, bottom, left, right,
        cv2.BORDER_CONSTANT, value=(0, 0, 0)
    )

def generate_output_filename(input_path: str, output_dir: str, suffix: str = "_processed") -> str:
    """生成唯一输出文件名"""
    input_file = Path(input_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices("abcdefghijkmnpqrstuvwxyz0123456789", k=4))
    output_file = f"{input_file.stem}{suffix}_{timestamp}_{random_str}{input_file.suffix}"
    return str(Path(output_dir) / output_file)

def cleanup_temp_files(temp_dir: str):
    """清理临时文件目录"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logger.error(f"清理临时文件失败: {str(e)}")

def validate_output_dir(output_dir: str) -> bool:
    """验证输出目录是否有效"""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        test_file = Path(output_dir) / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception as e:
        logger.error(f"输出目录不可写: {str(e)}")
        return False

def process_progress_callback(current: int, total: int):
    """处理进度回调示例"""
    progress = (current / total) * 100
    logger.info(f"处理进度: {progress:.1f}% ({current}/{total})")

def get_frame_preview(video_path: str, frame_num: int = 0) -> Optional[cv2.Mat]:
    """获取指定帧的预览图像"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_num >= total_frames:
            frame_num = total_frames - 1
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None
    except Exception as e:
        logger.error(f"获取预览帧失败: {str(e)}")
        return None

def codec_to_string(codec: int) -> str:
    """将FourCC编码转换为字符串"""
    return "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])

def format_duration(seconds: float) -> str:
    """格式化视频时长"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"