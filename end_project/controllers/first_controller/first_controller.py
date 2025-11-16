from controller import Robot, DistanceSensor, Motor, Camera
import sounddevice as sd
import queue
from vosk import Model, KaldiRecognizer
import json
import os

TIME_STEP = 64
MAX_SPEED = 6.28
SPEED = 4

# Initialize robot
robot = Robot()

# ---------------- SENSORS ----------------
# Distance sensors
ds = []
for i in range(8):
    ds.append(robot.getDevice('ps' + str(i)))
    ds[i].enable(TIME_STEP)

# Camera
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
width = camera.getWidth()
height = camera.getHeight()

# Motors
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)

# ---------------- VOICE SETUP ----------------
q = queue.Queue()
model = Model("model")  # vosk model folder
recognizer = KaldiRecognizer(model, 16000, '["straight","left","right","stop","search"]')

def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))

stream = sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=audio_callback)
stream.start()

# ---------------- COLOR DETECTION ----------------
RED, GREEN, BLUE, NONE = 0, 1, 2, 3
color_names = ["red", "green", "blue"]
filenames = ["red_blob.png", "green_blob.png", "blue_blob.png"]
ANSI_COLOR_RED = "\x1b[31m"
ANSI_COLOR_GREEN = "\x1b[32m"
ANSI_COLOR_BLUE = "\x1b[34m"
ANSI_COLOR_RESET = "\x1b[0m"
ansi_colors = [ANSI_COLOR_RED, ANSI_COLOR_GREEN, ANSI_COLOR_BLUE]

# ---------------- STATE ----------------
state = "FOLLOW"  # FOLLOW, AVOID, SEARCH
search_active = False
pause_counter = 0
left_speed = 0
right_speed = 0

# ---------------- MAIN LOOP ----------------
while robot.step(TIME_STEP) != -1:
    dvals = [x.getValue() for x in ds]

    # --- Voice commands ---
    if not q.empty():
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            command = result.get("text", "").lower()
            if command:
                print("Heard:", command)

                if "straight" in command:
                    left_speed = 0.5 * MAX_SPEED
                    right_speed = 0.5 * MAX_SPEED
                    search_active = False
                elif "left" in command:
                    left_speed = -0.5 * MAX_SPEED
                    right_speed = 0.5 * MAX_SPEED
                    search_active = False
                elif "right" in command:
                    left_speed = 0.5 * MAX_SPEED
                    right_speed = -0.5 * MAX_SPEED
                    search_active = False
                elif "stop" in command:
                    left_speed = 0
                    right_speed = 0
                    search_active = False
                elif "search" in command:
                    search_active = True
                    state = "SEARCH"
                    print("Starting color search!")

    # --- OBSTACLE AVOIDANCE ---
    if max(dvals) > 80:
        state = "AVOID"

    if state == "AVOID":
        right_obstacle = dvals[0] > 80 or dvals[1] > 80 or dvals[2] > 80
        left_obstacle = dvals[5] > 80 or dvals[6] > 80 or dvals[7] > 80

        if left_obstacle:
            left_speed = 0.5 * MAX_SPEED
            right_speed = -0.5 * MAX_SPEED
        elif right_obstacle:
            left_speed = -0.5 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED
        else:
            left_speed = 0.5 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED

        if max(dvals) < 80:
            state = "FOLLOW"

    # --- COLOR SEARCH ---
    elif search_active and state == "SEARCH":
        image = camera.getImage()

        if pause_counter > 0:
            pause_counter -= 1

        if pause_counter > 640 / TIME_STEP:
            left_speed = 0
            right_speed = 0
        elif pause_counter > 0:
            left_speed = -SPEED
            right_speed = SPEED
        elif image is None:
            left_speed = 0
            right_speed = 0
        else:
            red_sum = green_sum = blue_sum = 0
            for i in range(width // 3, 2 * width // 3):
                for j in range(height // 2, 3 * height // 4):
                    red_sum += camera.imageGetRed(image, width, i, j)
                    green_sum += camera.imageGetGreen(image, width, i, j)
                    blue_sum += camera.imageGetBlue(image, width, i, j)

            if red_sum > 3 * green_sum and red_sum > 3 * blue_sum:
                current_blob = RED
            elif green_sum > 3 * red_sum and green_sum > 3 * blue_sum:
                current_blob = GREEN
            elif blue_sum > 3 * red_sum and blue_sum > 3 * green_sum:
                current_blob = BLUE
            else:
                current_blob = NONE

            if current_blob == NONE:
                left_speed = -SPEED
                right_speed = SPEED
            else:
                left_speed = 0
                right_speed = 0
                print(f"Looks like I found a {ansi_colors[current_blob]}{color_names[current_blob]}{ANSI_COLOR_RESET} blob.")
                home_dir = os.path.expanduser("~")
                filepath = os.path.join(home_dir, filenames[current_blob])
                camera.saveImage(filepath, 100)
                pause_counter = 1280 / TIME_STEP

    # --- FOLLOWING MANUAL VOICE COMMAND ---
    elif state == "FOLLOW":
        pass  # speeds are already set by voice commands

    # Set motors
    leftMotor.setVelocity(left_speed)
    rightMotor.setVelocity(right_speed)
