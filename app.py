from PIL import Image, ImageDraw
import face_recognition
import subprocess
import sys

input_image = "sample/capture.jpg"
output_image = "sample/face.jpg"

capture_path = "sample/capture.jpg"

ERROR_LIMIT = 10
error_count = 0
fbi_pid = None


def loop():
    reset_error_count()
    capture_image_to_path(capture_path)
    image = face_recognition.load_image_file(input_image)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) == 0:
        return

    face_landmarks_list = face_recognition.face_landmarks(image, face_locations=face_locations[:1])

    if len(face_landmarks_list) == 0:
        print('No landmarks for found face')
        return
    face_location = face_locations[0]
    face_landmarks = face_landmarks_list[0]
    capture_image = Image.fromarray(image)
    pil_image = Image.new('RGBA', capture_image.size, color=(255, 255, 255, 255))
    d = ImageDraw.Draw(pil_image, 'RGBA')

    # Make the eyebrows into a nightmare
    brow_fill = (0, 0, 0, 128)
    brow_line = (0, 0, 0, 150)
    d.polygon(face_landmarks['left_eyebrow'], fill=brow_fill)
    d.polygon(face_landmarks['right_eyebrow'], fill=brow_fill)
    d.line(face_landmarks['left_eyebrow'], fill=brow_line, width=5)
    d.line(face_landmarks['right_eyebrow'], fill=brow_line, width=5)

    # Gloss the lips
    lip_fill = (0, 0, 0, 128)
    lip_line = (0, 0, 0, 64)
    d.polygon(face_landmarks['top_lip'], fill=lip_fill)
    d.polygon(face_landmarks['bottom_lip'], fill=lip_fill)
    d.line(face_landmarks['top_lip'], fill=lip_line, width=8)
    d.line(face_landmarks['bottom_lip'], fill=lip_line, width=8)

    # # Sparkle the eyes
    # eye_fill = (255, 255, 255, 30)
    # d.polygon(face_landmarks['left_eye'], fill=eye_fill)
    # d.polygon(face_landmarks['right_eye'], fill=eye_fill)
    #
    # # Apply some eyeliner
    # d.line(face_landmarks['left_eye'] + [face_landmarks['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
    # d.line(face_landmarks['right_eye'] + [face_landmarks['right_eye'][0]], fill=(0, 0, 0, 110), width=6)

    face = pil_image.crop((face_location[3], face_location[0], face_location[1], face_location[2]))
    face.save(output_image)
    set_drawn_image(output_image)


# Captures image from webcam and saves to the specified path
def capture_image_to_path(path):
    retry = True
    while retry:
        try:
            subprocess.run(['fswebcam', '-r', '320x240', '-q', '--no-banner', '--save', path], check=True)
            retry = False
        except subprocess.CalledProcessError as e:
            error(e)


# Set drawn image
def set_drawn_image(path):
    subprocess.run(['killall', 'fbi'])
    retry = True
    while retry:
        try:
            subprocess.run(['fbi', '-T', '2', '-a', output_image], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            retry = False
        except subprocess.CalledProcessError as e:
            error(e)


def reset_error_count():
    global error_count
    error_count = 0


def error(e):
    global error_count
    print('Error: {}'.format(e))
    error_count += 1
    if error_count == ERROR_LIMIT:
        sys.exit()


print('Running main loop...')
while True:
    loop()
