import matplotlib.pyplot as plt
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
    # duration of passage
    duration = fit_times[-1]-fit_times[0]
    # Jumping height(cm)
    height = cal_height(duration)
    # Draw a comparison chart
    plt.figure(figsize=(10, 5))
    plt.scatter(filtered_times, filtered_heights, color='b', label='Cleaned Ankle Data')
    plt.plot(fit_times, fit_heights, color='r', linestyle='-', label=f'Polyfit: h = {coeffs[0]:.2f} t^2 + {coeffs[1]:.2f} t + {coeffs[2]:.2f}')
    plt.xlabel('Time (s)')
    plt.ylabel('Relative Height')
    plt.title('Jump Motion Polynomial Fitting')
    plt.legend()
    plt.grid()
    plt.text(0.3, 0.1, f"Estimated Jump Height: {height:.2f} cm", fontsize=12, ha='left', color='red')
    plt.text(0.8, 0.1, f"Duration of Passage: {duration:.2f} s", fontsize=12, ha='left', color='green')
    print(
        f'\nEstimated Jump Height: {height:.2f} cm',
        f'\nDuration of Passage: {duration:.2f} s'
    )
    plt.show()
