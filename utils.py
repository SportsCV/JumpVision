import cv2
import numpy as np
from rtmlib import Body

openpose_skeleton = True  # True for openpose-style, False for mmpose-style
device = 'mps'  # cpu, cuda, mps
backend = 'onnxruntime'  # opencv, onnxruntime, openvino
ankle_indices = [10, 13]
body = Body(to_openpose=openpose_skeleton, mode='balanced', backend=backend, device=device)

g = 9.81  # m/s²


def free_fall(t, h0):
    return 0.5 * g * t ** 2 + h0


def cal_height(t):
    return (0.5 * g * (t / 2) ** 2) * 100


def draw_points(img, keypoints, scores):
    for idx in ankle_indices:
        if len(keypoints[0]) > idx and scores[0][idx] > 0.5:
            x, y = int(keypoints[0][idx][0]), int(keypoints[0][idx][1])
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)  # Draw a red dot to mark the ankle joint


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
        img_show = frame.copy()

        # Only draw ankle joint
        draw_points(img_show, keypoints, scores)

        # Obtain the position of the ankle joint
        left_ankle = keypoints[0][10] if len(keypoints[0]) > 10 else None
        right_ankle = keypoints[0][13] if len(keypoints[0]) > 13 else None

        if left_ankle is not None and right_ankle is not None:
            # Take the average vertical axis of the left and right ankle joints
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            # Reverse the Y coordinate
            ankle_y = frame.shape[0] - ankle_y
            ankle_y_coords.append(ankle_y)
            frame_times.append(time_elapsed)

        time_elapsed += 1 / fps

        cv2.imshow('Tracking', img_show)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return frame_times, ankle_y_coords


def clean_frame(frame_times, ankle_y_coords):
    # Data cleaning: identifying jump intervals
    y_diff = np.diff(ankle_y_coords)  # Calculate the change in adjacent points
    jump_start = np.where(y_diff > 5)[0][0]  # Find the first obvious point of increase
    jump_end = np.where(ankle_y_coords[jump_start:] < ankle_y_coords[jump_start])[0][0] + jump_start

    filtered_times = frame_times[jump_start:jump_end]
    filtered_heights = ankle_y_coords[jump_start:jump_end]

    # The height of the initial point
    initial_ankle_y = filtered_heights[0]
    # Relative height
    filtered_heights = [y - initial_ankle_y for y in filtered_heights]

    x_data = np.array(filtered_times) - filtered_times[0]
    y_data = np.array(filtered_heights)

    return x_data, y_data, filtered_times, filtered_heights


def fit_data(x_data, y_data, filtered_times):
    # Quadratic polynomial fitting
    coeffs = np.polyfit(x_data, y_data, 2)

    fit_times = np.linspace(filtered_times[0], filtered_times[-1], 100)
    fit_heights = np.polyval(coeffs, fit_times - filtered_times[0])

    return coeffs, fit_times, fit_heights
