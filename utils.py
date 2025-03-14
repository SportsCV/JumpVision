import cv2
import numpy as np
from rtmlib import Wholebody, draw_skeleton, Body

openpose_skeleton = True  # True for openpose-style, False for mmpose-style
device = 'mps'  # cpu, cuda, mps
backend = 'onnxruntime'  # opencv, onnxruntime, openvino
ankle_indices = [10, 13]
body = Body(to_openpose=openpose_skeleton, mode='balanced', backend=backend, device=device)

g = 9.81  # m/s²


def free_fall(t, h0):
    return 0.5 * g * t ** 2 + h0


def cal_height(t):
    return (0.5 * g * (t/2)**2) * 100


def draw_points(img, keypoints, scores):
    for idx in ankle_indices:
        if len(keypoints[0]) > idx and scores[0][idx] > 0.5:
            x, y = int(keypoints[0][idx][0]), int(keypoints[0][idx][1])
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)  # 画红色圆点标注踝关节


def video_parser(video_path: str):
    ankle_y_coords = []  # coordinates of the ankle
    frame_times = []  # frame time

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    time_elapsed = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        keypoints, scores = body(frame)
        img_show = frame.copy()  # 显示原图

        # 仅绘制踝关节（假设踝关节索引是10和11，需根据模型调整）
        draw_points(img_show, keypoints, scores)

        # 获取踝关节的点位（假设踝关节索引是10或13，需根据模型调整）
        left_ankle = keypoints[0][10] if len(keypoints[0]) > 10 else None
        right_ankle = keypoints[0][13] if len(keypoints[0]) > 13 else None

        if left_ankle is not None and right_ankle is not None:
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2  # 取左右踝关节的平均纵坐标
            # 反转 Y 坐标，确保竖直向上为正
            ankle_y = frame.shape[0] - ankle_y
            ankle_y_coords.append(ankle_y)
            frame_times.append(time_elapsed)

        time_elapsed += 1 / fps  # 计算当前帧的时间

        cv2.imshow('Tracking', img_show)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return frame_times, ankle_y_coords


def clean_frame(frame_times, ankle_y_coords):
    # 数据清洗：识别跳跃区间
    y_diff = np.diff(ankle_y_coords)  # 计算相邻点的变化量
    jump_start = np.where(y_diff > 5)[0][0]  # 找到第一个明显上升的点
    jump_end = np.where(ankle_y_coords[jump_start:] < ankle_y_coords[jump_start])[0][0] + jump_start  # 找到回落到起始高度的位置

    # 仅保留跳跃过程的数据
    filtered_times = frame_times[jump_start:jump_end]
    filtered_heights = ankle_y_coords[jump_start:jump_end]

    # 设置起始点为零
    initial_ankle_y = filtered_heights[0]  # 初始点的高度
    filtered_heights = [y - initial_ankle_y for y in filtered_heights]  # 相对高度

    x_data = np.array(filtered_times) - filtered_times[0]  # 确保从 t=0 开始
    y_data = np.array(filtered_heights)

    return x_data, y_data, filtered_times, filtered_heights


def fit_data(x_data, y_data, filtered_times):
    # 使用二次多项式拟合
    coeffs = np.polyfit(x_data, y_data, 2)  # 二次多项式拟合

    # 生成拟合曲线
    fit_times = np.linspace(filtered_times[0], filtered_times[-1], 100)
    fit_heights = np.polyval(coeffs, fit_times - filtered_times[0])

    return coeffs, fit_times, fit_heights
