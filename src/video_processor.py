import cv2
import numpy as np
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

class VideoProcessor:
    def __init__(self):
        pass
    
    def process_video(self, input_path, output_path, options):
        """
        处理单个视频文件
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
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
            
            if options.get("filter"):
                processed_frame = self.apply_filter(processed_frame, options.get("filter_type", "random"))
            
            if options.get("mirror") and random.random() < 0.3:
                processed_frame = self.apply_mirror(processed_frame)
            
            if options.get("speed") and random.random() < 0.3:
                frame_index = self.apply_speed_effect(cap, frame_index, total_frames, options)
            
            if options.get("shake") and random.random() < 0.1:
                processed_frame = self.apply_shake(processed_frame)
            
            if options.get("framedrop") and random.random() < 0.05:
                frame_index += random.randint(1, 3)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                continue
            
            # 写入处理后的帧
            out.write(processed_frame)
            frame_index += 1
        
        cap.release()
        out.release()
        return True
    
    def process_multiple_videos(self, video_paths, output_path, options):
        """
        处理多个视频进行混剪
        """
        clips = []
        
        # 读取所有视频片段
        for path in video_paths:
            if os.path.exists(path):
                clip = VideoFileClip(path)
                
                # 应用随机裁剪效果
                if options.get("crop"):
                    clip = self.apply_random_crop(clip, options.get("crop_percent", 15))
                
                clips.append(clip)
        
        # 合成视频
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
        
        return True
    
    # 下面是各种效果处理方法示例
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
            filter_type = random.choice(["gaussian", "sepia", "contrast"])
            
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
        
        if new_frame < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        else:
            new_frame = total_frames - 1
            
        return new_frame
    
    def apply_shake(self, frame):
        """应用随机抖动效果"""
        height, width = frame.shape[:2]
        
        # 随机抖动幅度
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        
        # 创建变换矩阵
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        
        # 应用仿射变换
        return cv2.warpAffine(frame, M, (width, height))
    
    def apply_random_crop(self, clip, percent=15):
        """对视频剪辑应用随机裁剪"""
        width, height = clip.size
        
        crop_w = int(width * percent / 100)
        crop_h = int(height * percent / 100)
        
        def crop_func(get_frame, t):
            frame = get_frame(t)
            start_x = random.randint(0, crop_w)
            start_y = random.randint(0, crop_h)
            end_x = width - random.randint(0, crop_w)
            end_y = height - random.randint(0, crop_h)
            
            cropped = frame[start_y:end_y, start_x:end_x]
            return cv2.resize(cropped, (width, height))
        
        return clip.fl(crop_func)