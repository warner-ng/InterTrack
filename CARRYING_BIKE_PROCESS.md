# CarryingBike Motion Data Processing

## 快速开始

### 前置准备
- ✅ 已提取 145 帧 RGB 视频
- ✅ 已生成人物和物体掩码
- ✅ 已下载 InterTrack 模型

### 执行流程

#### 1. 运行 InterTrack 完整推理管道 (4 阶段)

```bash
bash scripts/run_carrying_bike_pipeline.sh
```

这将执行：
- **Stage 1**: 点云重建 (HDM)
- **Stage 2**: 点云精化 (HDM with attention)
- **Stage 3**: 人体 SMPL 对应 (CorrAE)
- **Stage 4**: 人体 SMPL 优化

输出保存在 `outputs/` 目录下

预计耗时：**1-2 小时** (GPU dependent)

#### 2. 转换为 ResMimic 格式

```bash
python convert_intertrack_to_resmimic.py
```

这将生成：
- `carrying_bike_human.pkl` - 人体 SMPL 运动数据
- `carrying_bike_object.npz` - 物体 3D 位置和旋转

#### 3. (可选) 复制到 ResMimic

```bash
cp carrying_bike_human.pkl /home/warner/_projects/ResMimic/assets/motions/
cp carrying_bike_object.npz /home/warner/_projects/ResMimic/assets/motions/
```

## 工具脚本

### improve_masks.py
重新生成去掩码（如果需要提高质量）

```bash
python improve_masks.py
```

### 配置文件
- `demo-data/carrying_bike/split_carrying_bike.pkl` - 数据分割配置
- `demo-data/carrying_bike/camera_calibration.pkl` - 相机参数

## 数据结构

```
demo-data/carrying_bike/
├── frames/
│   ├── frame_00001.color.jpg           (RGB 帧)
│   ├── frame_00001.person_mask.png     (人物掩码)
│   ├── frame_00001.obj_rend_mask.png   (物体掩码)
│   └── ...
├── split_carrying_bike.pkl             (InterTrack split 配置)
└── camera_calibration.pkl              (相机参数)
```

## 注意事项

1. 确保在 `intertrack` 虚拟环境中运行
2. 需要 GPU 加速（可用 CPU 但会很慢）
3. 第 1 和 2 阶段的参数已针对掩码质量优化
4. 完整管道包括联合优化人体和物体

## 输出文件

运行完整管道后：
- 人体点云：`outputs/stage2-*/single/*/pred/*.hum.npy`
- 物体点云：`outputs/stage2-*/single/*/pred/*.obj.npy`
- SMPL 参数：`outputs/corrAE/single/opt-hum-*/...`
- 优化结果：`outputs/corrAE/single/opt-hum-*/...`
