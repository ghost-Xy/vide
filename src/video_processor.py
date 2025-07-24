import cv2
import numpy as np
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageSequenceClip
import os
import time
from tqdm import tqdm
from . import utils

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "temp_frames"
    
    def process_video(self, input_path, output_path, options, progress_callback=None):
        """
        处理单个视频文件
        """
        # 验证输出目录
        if not utils.validate_output_dir(os.path.dirname(output_path)):
            return False
        
        # 获取视频信息
        video_info = utils.get_video_info(input_path)
        if not video_info:
            return False
        
        # 创建临时目录
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 处理流程
        try:
            # 开始时间
            start_time = time.time()
            
            # 处理视频
            frames = []
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                return False
            
            width = video_info['width']
            height = video_info['height']
            fps = video_info['fps']
            total_frames = video_info['frame_count']
            
            # 准备输出视频
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # 应用所有选中的效果
            frame_index = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                processed_frame = frame.copy()
                
                # 应用去重效果
                if options.get("crop"):
                    processed_frame = self.apply_crop(processed_frame, options.get("crop_percent", 15))
                
                if options.get("filter") and random.random() < 0.7:
                    processed_frame = self.apply_filter(processed_frame, options.get("filter_type", "random"))
                
                if options.get("mirror") and random.random() < 0.3:
                    processed_frame = self.apply_mirror(processed_frame)
                
                if options.get("speed") and random.random() < 0.3:
                    frame_index = self.apply_speed_effect(cap, frame_index, total_frames, options)
                    continue
                
                if options.get("shake") and random.random() < 0.1:
                    processed_frame = self.apply_shake(processed_frame)
                
                if options.get("framedrop") and random.random() < 0.05:
                    frame_index += random.randint(1, 3)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                    continue
                
                # 写入处理后的帧
                out.write(processed_frame)
                frame_index += 1
                
                # 更新进度
                if progress_callback:
                    progress = int((frame_index / total_frames) * 100)
                    progress_callback(progress)
            
            # 释放资源
            cap.release()
            out.release()
            
            # 处理时长
            duration = time.time() - start_time
            print(f"视频处理完成 - 时长: {duration:.2f}秒")
            return True
        
        except Exception as e:
            print(f"处理视频时出错: {str(e)}")
            return False
        finally:
            # 清理临时文件
            utils.cleanup_temp_files(self.temp_dir)
    
    def process_multiple_videos(self, video_paths, output_path, options):
        """
        处理多个视频进行混剪
        """
        try:
            if not video_paths:
                return False
                
            # 验证输出目录
            if not utils.validate_output_dir(os.path.dirname(output_path)):
                return False
                
            # 创建临时目录
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # 开始混剪处理
            start_time = time.time()
            clips = []
            
            # 处理每个视频片段
            for idx, path in enumerate(video_paths):
                if not os.path.exists(path):
                    continue
                    
                print(f"处理视频 {idx+1}/{len(video_paths)}: {os.path.basename(path)}")
                
                # 处理单个视频
                temp_output = os.path.join(self.temp_dir, f"temp_{idx}.mp4")
                success = self.process_video(path, temp_output, options)
                
                if success:
                    clip = VideoFileClip(temp_output)
                    clips.append(clip)
            
            # 合成视频
            if clips:
                if options.get("combo_method") == "random":
                    random.shuffle(clips)
                    final_clip = concatenate_videoclips(clips, method="compose")
                elif options.get("combo_method") == "scene_reorg":
                    # 场景重组逻辑（简化版）
                    final_clip = self.scene_reorganization(clips)
                else:  # 默认顺序合成
                    final_clip = concatenate_videoclips(clips, method="compose")
                
                # 设置输出参数
                final_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=30,
                    threads=4,
                    preset='fast'
                )
                
                duration = time.time() - start_time
                print(f"混剪完成 - 总时长: {duration:.2f}秒")
                return True
            return False
            
        except Exception as e:
            print(f"混剪视频时出错: {str(e)}")
            return False
        finally:
            # 清理临时文件
            utils.cleanup_temp_files(self.temp_dir)
    
    # 下面是各种效果处理方法
    def apply_crop(self, frame, percent=15):
        """随机裁剪视频内容"""
        height, width = frame.shape[:2]
        crop_x = int(width * percent / 100)
        crop_y = int(height * percent / 100)
        
        # 随机选择裁剪位置
        start_x = random.randint(0, crop_x)
        start_y = random.randint(0, crop_y)
        end_x = width - random.randint(0, crop_x)
        end_y = height - random.randint(0, crop_y)
        
        cropped_frame = frame[start_y:end_y, start_x:end_x]
        
        # 将裁剪后的帧调整回原始尺寸
        return cv2.resize(cropped_frame, (width, height))
    
    def apply_filter(self, frame, filter_type="random"):
        """应用随机滤镜效果"""
        if filter_type == "random":
            filter_type = random.choice(["gaussian", "sepia", "contrast", "hsv_shift"])
            
        if filter_type == "gaussian":
            return cv2.GaussianBlur(frame, (5, 5), 0)
        elif filter_type == "sepia":
            # 应用棕褐色滤镜
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                                     [0.349, 0.686, 0.168],
                                     [0.393, 0.769, 0.189]])
            return cv2.transform(frame, sepia_filter)
        elif filter_type == "contrast":
            # 增加对比度
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        elif filter_type == "hsv_shift":
            # 随机HSV偏移
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[:,:,0] = (hsv[:,:,0] + random.randint(-10, 10)) % 180
            hsv[:,:,1] = np.clip(hsv[:,:,1] + random.randint(-20, 20), 0, 255)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        else:
            return frame
    
    def apply_mirror(self, frame):
        """水平镜像效果"""
        return cv2.flip(frame, 1)
    
    def apply_speed_effect(self, cap, current_frame, total_frames, options):
        """随机跳过帧实现变速效果"""
        min_speed = options.get("min_speed", 0.9)
        max_speed = options.get("max_speed", 1.1)
        
        # 随机决定跳过多少帧
        skip_frames = random.randint(0, int(min_speed * 10)) if min_speed < 1.0 else 0
        skip_frames += random.randint(0, int(max_speed * 10) - 10) if max_speed > 1.0 else 0
        
        new_frame = current_frame + skip_frames
        
        if new_frame < total_frames