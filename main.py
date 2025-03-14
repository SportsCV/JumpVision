import matplotlib.pyplot as plt
import numpy as np

from utils import video_parser, clean_frame, fit_data, cal_height


if __name__ == '__main__':
    # test video
    video_path = 'demo1.mp4'
    # parse key points
    frame_times, ankle_y_coords = video_parser(video_path)
    # Extract the start and end frames of the jump
    x_data, y_data, filtered_times, filtered_heights = clean_frame(frame_times, ankle_y_coords)
    # Fit the relationship between h and t based on a quadratic function
    coeffs, fit_times, fit_heights = fit_data(x_data, y_data, filtered_times)
    # Flight time
    duration = fit_times[-1]-fit_times[0]
    # Jumping height(cm)
    height = cal_height(duration)
    max_height = np.max(fit_heights)
    cm_per_pixel = height / max_height
    filtered_heights = [y * cm_per_pixel for y in filtered_heights]
    fit_heights = [y * cm_per_pixel for y in fit_heights]    # Draw a comparison chart
    plt.figure(figsize=(10, 5))
    plt.scatter(filtered_times, filtered_heights, color='b', label='Cleaned Ankle Data')
    plt.plot(fit_times, fit_heights, color='r', linestyle='-', label=f'Polyfit: h = {coeffs[0]*cm_per_pixel:.2f} t^2 + {coeffs[1]*cm_per_pixel:.2f} t + {coeffs[2]*cm_per_pixel:.2f}')
    plt.xlabel('Time (s)')
    plt.ylabel('Relative Height(cm)')
    plt.title('Jump Motion Polynomial Fitting')
    plt.legend()
    plt.grid()
    plt.text(0.01, 0.95, f"Jump Height: {height:.2f} cm",
             fontsize=12, ha='left', va='top', color='red',
             transform=plt.gca().transAxes)

    plt.text(0.01, 0.90, f"Flight Time: {duration:.2f} s",
             fontsize=12, ha='left', va='top', color='green',
             transform=plt.gca().transAxes)

    plt.text(0.01, 0.85, f"Max velocity: {coeffs[1] * cm_per_pixel / 100:.2f} m/s",
             fontsize=12, ha='left', va='top', color='blue',
             transform=plt.gca().transAxes)
    print(
        f'\nJump Height: {height:.2f} cm',
        f'\nFlight Time: {duration:.2f} s',
        f'\nMax velocity: {coeffs[1]*cm_per_pixel/100:.2f} m/s'
    )
    plt.show()
