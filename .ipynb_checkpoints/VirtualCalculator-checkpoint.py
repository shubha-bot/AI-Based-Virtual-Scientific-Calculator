# VirtualCalculator.py
import cv2
import numpy as np
from HandTrackingModule import HandDetector
import pygame
import math
import re

# -------- Initialize pygame mixer for sound --------
pygame.mixer.init()
click_sound = pygame.mixer.Sound("click.wav")
answer_sound = pygame.mixer.Sound("answer.wav")

# -------- Button Class --------
class Button:
    def __init__(self, pos, width, height, label, insert=None):
        self.pos = pos
        self.width = width
        self.height = height
        self.label = label
        self.insert = insert or label

    def draw(self, img):
        x, y = self.pos
        cv2.rectangle(img, (x, y), (x + self.width, y + self.height),
                      (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + self.width, y + self.height),
                      (255, 255, 255), 2)
        cv2.putText(img, self.label, (x + 18, y + 62),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    def checkClick(self, x, y):
        return (self.pos[0] < x < self.pos[0] + self.width and
                self.pos[1] < y < self.pos[1] + self.height)

# -------- Create Buttons --------
buttonList = []

# Standard buttons (4x4)
std_values = [["7", "8", "9", "/"],
              ["4", "5", "6", "*"],
              ["1", "2", "3", "-"],
              ["C", "0", "=", "+"]]

for i in range(4):
    for j in range(4):
        buttonList.append(Button([100 * j + 50, 100 * i + 150],
                                 100, 100, std_values[i][j]))

# Scientific buttons (5x4) – added nCr, x^-1, comma, (, ), x^2, x^3
sci_buttons = [
    [("^", "^"), ("sqrt", "sqrt("), (".", "."), ("cbrt", "cbrt("), ("(", "(")],
    [("exp", "exp("), ("log", "log("), ("ln", "ln("), ("pi", "pi"), (")", ")")],
    [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("e", "e"), ("x^2", "**2")],
    [("!", "factorial("), ("nCr", "math.comb("), ("x^-1", "1/("), (",", ","), ("x^3", "**3")]
]

for i in range(len(sci_buttons)):
    for j in range(len(sci_buttons[i])):
        label, ins = sci_buttons[i][j]
        if label != "":
            buttonList.append(Button([100 * j + 500, 100 * i + 150],
                                     100, 100, label, ins))

# -------- Convert equation to Python expression --------
def to_python_expr(eq: str) -> str:
    expr = eq

    # Operators & constants
    expr = expr.replace("^", "**")
    expr = expr.replace("pi", "np.pi")
    expr = re.sub(r"\be\b", "np.e", expr)  # replace only standalone 'e'

    # Math functions
    replacements = {
        "sqrt(": "np.sqrt(",
        "cbrt(": "np.cbrt(",
        "exp(": "np.exp(",
        "log(": "np.log10(",
        "ln(": "np.log(",
        "factorial(": "math.factorial(",
        "sin(": "np.sin(np.radians(",
        "cos(": "np.cos(np.radians(",
        "tan(": "np.tan(np.radians(",
        "math.comb(": "math.comb(",
        "1/(": "1/("
    }

    for k, v in replacements.items():
        expr = expr.replace(k, v)

    # Auto-close parentheses
    opens = expr.count("(")
    closes = expr.count(")")
    if opens > closes:
        expr += ")" * (opens - closes)

    return expr

# -------- Variables --------
equation = ""
delayCounter = 0
smooth_x, smooth_y = 0, 0
alpha = 0.2

# -------- Webcam --------
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, flipType=True)

    for button in buttonList:
        button.draw(img)

    cv2.rectangle(img, (50, 50), (1100, 150), (255, 255, 255), cv2.FILLED)
    cv2.putText(img, equation, (60, 120),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

    if hands:
        lmList = hands[0]["lmList"]
        if lmList:
            raw_x, raw_y = lmList[8][1], lmList[8][2]
            smooth_x = int(smooth_x * (1 - alpha) + raw_x * alpha)
            smooth_y = int(smooth_y * (1 - alpha) + raw_y * alpha)
            cv2.circle(img, (smooth_x, smooth_y), 10, (0, 255, 0), cv2.FILLED)

            for button in buttonList:
                if button.checkClick(smooth_x, smooth_y) and delayCounter == 0:
                    val = button.insert
                    if val == "=":
                        try:
                            expr = to_python_expr(equation)
                            result = eval(expr, {"np": np, "math": math, "__builtins__": {}})
                            equation = str(result)
                            answer_sound.play()
                        except Exception:
                            equation = "Error"
                            answer_sound.play()
                    elif val == "C":
                        equation = ""
                        click_sound.play()
                    else:
                        equation += val
                        click_sound.play()
                    delayCounter = 1

    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 50:
            delayCounter = 0

    cv2.imshow("Virtual Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
