import sys
import os
import torch

sys.path.insert(0, os.path.abspath('mmaction2'))

from mmengine.config import Config
from mmaction.apis import init_recognizer, inference_recognizer
from utils.label_map import load_label_map

config_path = 'mmaction2/configs/recognition/tsn/tsn_imagenet-pretrained-r50_8xb32-1x1x3-100e_kinetics400-rgb.py'
checkpoint_path = 'tsn_config/tsn_r50_model.pth'

model = init_recognizer(
    config=config_path,
    checkpoint=checkpoint_path,
    device='cuda:0' if torch.cuda.is_available() else 'cpu'
)

label_map = load_label_map()

def classify_action_on_model(model, label_map, video_path: str) -> str:
    result = inference_recognizer(model, video_path)
    label_id = int(result.pred_label.item())
    score = float(result.pred_score[label_id])
    action_name = label_map[label_id]
    return f'{action_name} ({score:.2f})'

if __name__ == '__main__':
    video_file = 'sample/input.mp4'
    action = classify_action_on_model(model, label_map, video_file)
    print(f'🔍 偵測動作：{action}')
