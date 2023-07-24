import cv2
import numpy as np

# Video file path
video_file = '~/path/test_video.mp4'

# Output .c file path
output_c = '~/path/output_video.c'

# Output header file path
output_h = '~path/output_video.h'

# Output array name prefix
array_name_prefix = 'VIDEO_FRAME_'

# Video resolution
width, height = 128, 64

# Function to convert an 8x8 grayscale image to a hex string
def image_to_hex(image):
    hex_string = ""
    for row in range(8):
        value = 0
        for col in range(8):
            pixel = image[row, col]
            if pixel > 127:  # Threshold value for 1-bit conversion
                value |= 1 << (7 - col)
        hex_string += f"0x{value:02X},"
    return hex_string

def convert_video_to_hex(frame_start, frame_end):
    # Open the video file
    cap = cv2.VideoCapture(video_file)

    # Calculate the total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Frame range for conversion
    frame_start = 0  # Starting frame (inclusive)
    frame_end = 30 - 1  # Ending frame (inclusive)

    # Adjust frame range if necessary
    frame_start = max(0, min(frame_start, total_frames - 1))
    frame_end = max(frame_start, min(frame_end, total_frames - 1))

    # Open the output .c file for writing
    with open(output_c, 'w') as f_c, open(output_h, 'w') as f_h:
        # Write the header file includes
        f_h.write('#ifndef OUTPUT_H\n')
        f_h.write('#define OUTPUT_H\n\n')

        # Write the array declarations
        for frame_number in range(frame_start, frame_end + 1):
            array_name = f"{array_name_prefix}{frame_number}"
            f_c.write(f"const uint8_t {array_name}[{width * height // 8}] = {{\n")
            f_h.write(f"extern const uint8_t {array_name}[{width * height // 8}];\n")

            # Read the current frame from the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if not ret:
                break

            # Resize the frame to the desired resolution
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)

            # Convert the frame to grayscale
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Flatten the frame and store pixel values in the array
            frame_flat = frame_gray.flatten()
            frame_bytes = np.packbits(frame_flat > 127).tobytes()
            f_c.write(','.join([f"0x{byte:02X}" for byte in frame_bytes]))

            f_c.write('\n};\n\n')

        # Write the function to put each GRAPHICS_FRAME into a const uint8_t* array
        f_c.write(f"const uint8_t* GRAPHICS_SJOO_INTRO_VIDEO[{frame_end - frame_start + 1}] = {{\n")
        for frame_number in range(frame_start, frame_end + 1):
            array_name = f"{array_name_prefix}{frame_number}"
            f_c.write(f"{array_name},\n")
        f_c.write('    };\n')

        # Write the header file closing
        f_h.write('\n#endif\n')

    # Release the video file
    cap.release()

    print("Conversion complete.")

convert_video_to_hex(0, 30)