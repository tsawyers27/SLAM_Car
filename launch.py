import argparse
import subprocess

def main():
    # Define parser to add terminal arguments and modes
    parser = argparse.ArgumentParser()

    # Add arguments and values to parser
    parser.add_argument('--mode', type=str, required=True,
                        choices = ['lidar_test', 'slam', 'motor_test'])

    # Control flow logic for different modes
    args = parser.parse_args()

    if args.mode == 'lidar_test':
        subprocess.run(["ros2 launch rplidar_ros rplidar_a2m12_launch.py"])

if __name__ == '__main__':
    main()