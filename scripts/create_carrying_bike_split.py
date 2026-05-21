#!/usr/bin/env python3
"""
为 carrying_bike 数据创建 InterTrack split 文件
按照 InterTrack 的标准格式
"""
import pickle
from pathlib import Path

# 数据路径
demo_data_dir = Path("/home/warner/_projects/InterTrack/demo-data/carrying_bike")
frames_dir = demo_data_dir / "frames"

# 获取所有 RGB 帧
rgb_files = sorted(frames_dir.glob("frame_*.color.jpg"))
num_frames = len(rgb_files)

# 构建相对于项目根目录的路径列表
# InterTrack 期望的格式：list of relative file paths
test_frame_paths = []
for rgb_file in rgb_files:
    rel_path = str(rgb_file.relative_to(Path("/home/warner/_projects/InterTrack")))
    test_frame_paths.append(rel_path)

# 创建 split 字典（所有帧作为测试集，因为是推理模式）
split_dict = {
    'train': [],
    'test': test_frame_paths
}

# 保存为 pkl 文件
split_file = demo_data_dir / "split_carrying_bike.pkl"
with open(split_file, 'wb') as f:
    pickle.dump(split_dict, f)

print(f"✓ 已创建 split 文件: {split_file}")
print(f"  总帧数: {num_frames}")
print(f"  训练帧: {len(split_dict['train'])}")
print(f"  测试帧: {len(split_dict['test'])}")
print(f"\n使用方式:")
print(f"  python main.py dataset.split_file={split_file} \\")
print(f"                dataset.demo_data_path={demo_data_dir} ...")
