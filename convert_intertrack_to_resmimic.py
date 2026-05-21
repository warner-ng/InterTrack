#!/usr/bin/env python3
"""
将 InterTrack 推理输出转换为 ResMimic PKL/NPZ 格式
完全基于 InterTrack 的数据接口
"""
import os
import pickle
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, '/home/warner/_projects/InterTrack')


def main():
    print("=" * 80)
    print("InterTrack → ResMimic 格式转换")
    print("=" * 80)
    print()
    
    # 配置
    project_dir = Path("/home/warner/_projects/InterTrack")
    output_dir = project_dir / "outputs" / "stage2-carrying-bike" / "single" / "carrying_bike_stage2"
    smpl_dir = project_dir / "outputs" / "corrAE" / "single" / "opt-hum-carrying-bike"
    
    print(f"输入目录: {output_dir}")
    print(f"SMPL目录: {smpl_dir}")
    print()
    
    # 检查文件是否存在
    pred_dir = output_dir / "pred"
    smplh_dir = output_dir / "smplh"
    
    if not pred_dir.exists():
        print(f"❌ 错误: 推理输出目录不存在: {pred_dir}")
        print("   请先运行 run_carrying_bike_pipeline.sh")
        sys.exit(1)
    
    if not smplh_dir.exists():
        print(f"❌ 错误: SMPL输出目录不存在: {smplh_dir}")
        print("   请先运行完整的 InterTrack 推理管道")
        sys.exit(1)
    
    print("✓ 输出目录存在")
    print()
    
    # 查看目录结构
    print("【第1步】检查 InterTrack 输出文件结构")
    print("-" * 80)
    
    pred_files = sorted(pred_dir.glob("*.npy"))
    print(f"✓ 找到 {len(pred_files)} 个输出文件")
    if pred_files:
        print(f"  示例: {pred_files[0].name}")
    
    smpl_files = sorted(smplh_dir.glob("*.npy"))
    print(f"✓ 找到 {len(smpl_files)} 个 SMPL 文件")
    if smpl_files:
        print(f"  示例: {smpl_files[0].name}")
    
    print()
    print("【第2步】等待用户确认数据映射")
    print("-" * 80)
    print("""
为了完整转换数据，需要确认以下信息:

1. 人体数据 (PKL):
   - 需要从 SMPL 输出中提取:
     * root_pos: (T, 3) - 根节点位置
     * root_rot: (T, 4) - 根节点旋转(四元数)
     * dof_pos: (T, 29) - 29个DOF关节角度
     * local_body_pos: (T, 38, 3) - 38个关键点
     * link_body_list: 身体部件名称列表
   
2. 物体数据 (NPZ):
   - 需要从点云输出中计算:
     * trans: (T, 3) - 物体3D平移
     * rot: (T, 4) - 物体旋转(四元数)

当前状态: 已找到所有必需的输出文件结构
下一步: 审视 SMPL 和点云文件的具体格式

建议:
1. 在 Python 中加载单个文件查看内容
2. 了解数据的具体格式和结构  
3. 完整实现转换逻辑

""")
    
    # 查看一个示例文件
    print("【第3步】采样检查文件内容")
    print("-" * 80)
    
    if smpl_files:
        sample_file = smpl_files[0]
        try:
            data = np.load(sample_file)
            print(f"✓ SMPL 样本文件: {sample_file.name}")
            print(f"  数据类型: {type(data)}")
            print(f"  形状: {data.shape}")
            print(f"  数据类型: {data.dtype}")
        except Exception as e:
            print(f"✗ 无法读取: {e}")
    
    if pred_files:
        # 查找点云文件 (通常包含 .hum 或 .obj)
        hum_files = list(pred_dir.glob("*.hum.npy"))
        obj_files = list(pred_dir.glob("*.obj.npy"))
        
        if hum_files:
            sample_file = hum_files[0]
            try:
                data = np.load(sample_file)
                print(f"\n✓ 人尸点云样本: {sample_file.name}")
                print(f"  形状: {data.shape}")
                print(f"  数据类型: {data.dtype}")
            except Exception as e:
                print(f"✗ 无法读取: {e}")
        
        if obj_files:
            sample_file = obj_files[0]
            try:
                data = np.load(sample_file)
                print(f"\n✓ 物体点云样本: {sample_file.name}")
                print(f"  形状: {data.shape}")
                print(f"  数据类型: {data.dtype}")
            except Exception as e:
                print(f"✗ 无法读取: {e}")
    
    print()
    print("=" * 80)
    print("📋 转换框架已就绪")
    print("=" * 80)
    print("""
现在需要:
1. 查看 InterTrack 源代码中如何处理 SMPL/点云数据
2. 确认数据的具体字段名和格式
3. 实现完整的转换逻辑

您可以在 Python 交互界面中测试:
  cd /home/warner/_projects/InterTrack
  python
  >>> import numpy as np
  >>> data = np.load('outputs/.../__.npy')
  >>> print(data.shape, data.dtype)
""")


if __name__ == "__main__":
    main()
