#!/bin/bash
set -e

# InterTrack 完整推理管道 - carrying_bike 序列
# 基于官方的 demo_phone.sh 修改
# 输出将转换为 ResMimic format (PKL + NPZ)

# 项目配置
PROJECT_DIR=/home/warner/_projects/InterTrack
cd "$PROJECT_DIR"

# 数据文件
split_file="${PROJECT_DIR}/demo-data/carrying_bike/split_carrying_bike.pkl"
demo_data_path="${PROJECT_DIR}/demo-data/carrying_bike"

# 首先创建 split 文件
echo "Creating split file..."
python scripts/create_carrying_bike_split.py

# 颜色定义
GREEN=$'\e[0;32m'
RED=$'\e[0;31m'
NC=$'\e[0m'

echo ""
echo "${RED}========================================${NC}"
echo "${RED}InterTrack Pipeline - Carrying Bike${NC}"
echo "${RED}========================================${NC}"

# Stage 1: HDM 点云重建
echo ""
echo "${RED}Stage 1/4: HDM Point Cloud Reconstruction${NC}"
python main.py \
  run.name=stage1-carrying-bike \
  dataloader.batch_size=4 \
  model.model_name=pc2-diff-ho-sepsegm \
  model.predict_binary=True \
  dataset.split_file=${split_file} \
  dataset.demo_data_path=${demo_data_path} \
  run.job=sample \
  dataset.type=behave-test \
  run.save_name=carrying_bike \
  dataset.test_transl_type=estimated-2d \
  dataset.std_coverage=3.8 \
  run.sample_save_gt=False \
  run.diffusion_scheduler=ddim \
  run.num_inference_steps=50 \
  run.batch_start=0 \
  run.batch_end=145

# Stage 2: HDM 精化
echo ""
echo "${RED}Stage 2/4: HDM Refinement${NC}"
python main.py \
  run.name=stage2-carrying-bike \
  model=ho-attn \
  model.attn_weight=1.0 \
  model.attn_type=coord3d+posenc-learnable \
  model.point_visible_test=combine \
  dataset.split_file=${split_file} \
  dataset.demo_data_path=${demo_data_path} \
  dataloader.batch_size=4 \
  dataset.ho_segm_pred_path=${PROJECT_DIR}/outputs/stage1-carrying-bike/single/carrying_bike/pred \
  run.job=sample \
  run.sample_mode=interm-pred \
  run.sample_noise_step=500 \
  dataset.type=behave-attn-test \
  run.save_name=carrying_bike_stage2 \
  dataset.test_transl_type=estimated-2d \
  dataset.std_coverage=3.8 \
  run.sample_save_gt=False \
  run.diffusion_scheduler=ddim \
  run.num_inference_steps=50 \
  run.batch_start=0 \
  run.batch_end=145

# Stage 3: CorrAE - 人体 SMPL 对应
echo ""
echo "${RED}Stage 3/4: Human SMPL Correspondence (CorrAE)${NC}"
python main_corrae.py \
  run.name=humae-carrying-bike \
  model=pvcnn-ae \
  model.num_points=6890 \
  dataset=behave \
  dataset.fix_sample=True \
  dataset.type=behave-attn-test \
  dataloader.batch_size=16 \
  run.freeze_feature_model=False \
  dataset.split_file=${split_file} \
  run.job=sample \
  dataset.demo_data_path=${demo_data_path} \
  dataset.ho_segm_pred_path=${PROJECT_DIR}/outputs/stage2-carrying-bike/single/carrying_bike_stage2/pred \
  dataset.test_transl_type=estimated-2d \
  run.sample_mode=interm-hum \
  run.save_name=humae-carrying-bike \
  run.batch_start=0 \
  run.batch_end=145

# 创建 SMPL 链接以供优化使用
hdm_out=${PROJECT_DIR}/outputs/stage2-carrying-bike/single/carrying_bike_stage2
ln -sf ${PROJECT_DIR}/outputs/corrAE/single/humae-carrying-bike/smplh ${hdm_out}/smplh

# Stage 4: 人体 SMPL 优化
echo ""
echo "${RED}Stage 4/4: Human SMPL Optimization${NC}"
python main_humopt_smpl.py \
  run.name=opt-hum-carrying-bike \
  model=pvcnn-ae \
  model.num_points=6890 \
  dataset=behave \
  dataset.type=behave-attn-test \
  dataset.test_transl_type=estimated-2d \
  dataloader.batch_size=256 \
  run.job=sample \
  run.max_steps=5000 \
  logging.wandb=False \
  run.save_name=opt-hum-carrying-bike \
  model.hum_lw_cd=100 \
  model.hum_lw_rigid=1000 \
  model.hoi_lw_temp_h=1000 \
  model.hum_opt_s=True \
  model.hum_opt_t=True \
  dataset.split_file=${split_file} \
  dataset.demo_data_path=${demo_data_path} \
  dataset.ho_segm_pred_path=${hdm_out}/pred

# 完成
echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}✓ InterTrack pipeline completed!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "输出位置:"
echo "  Stage 1: ${PROJECT_DIR}/outputs/stage1-carrying-bike/"
echo "  Stage 2: ${PROJECT_DIR}/outputs/stage2-carrying-bike/"
echo "  CorrAE:  ${PROJECT_DIR}/outputs/corrAE/single/opt-hum-carrying-bike/"
echo ""
echo "下一步: 使用 convert_intertrack_to_resmimic.py 转换数据格式"
