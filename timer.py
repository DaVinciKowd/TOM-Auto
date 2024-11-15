import tkinter as tk
import math

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
DARK_RED = "#b22222"
DARK_GREEN = "#228b22"
WHITE = "#ffffff"
FONT_NAME = "Courier"
IMPACT_FONT = "Impact"
HANDWRITING_FONT = "Lucida Handwriting"
reps = 0
timer = None

def reset_timer():
    window.after_cancel(timer)
    canvas.itemconfig(timer_text, text="00:00")
    title_label.config(text="TIMER")
    check_marks.config(text="")
    global reps
    reps = 0

def start_timer():
    global reps
    reps += 1
    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60
    if reps % 8 == 0:
        count_down(long_break_sec)
        title_label.config(text="Time to Rest!", fg=WHITE)
    elif reps % 2 == 0:
        count_down(short_break_sec)
        title_label.config(text="Time to Rest!", fg=WHITE)
    else:
        count_down(work_sec)
        title_label.config(text="Working Time!", fg=WHITE)

def count_down(count):
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f"0{count_sec}"
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)  # Correct interval for 1 second
    else:
        start_timer()
        marks = ""
        work_sessions = math.floor(reps / 2)
        for _ in range(work_sessions):
            marks += "✔"
        check_marks.config(text=marks)

window = tk.Tk()
window.title("TOM-Auto - Pomodoro Timer")
window.config(padx=100, pady=50, bg=DARK_RED)

header_label = tk.Label(text="TOM-Auto", fg=DARK_GREEN, bg=DARK_RED, font=(HANDWRITING_FONT, 40, "bold"))
header_label.pack(pady=(10, 5))

subheader_label = tk.Label(text="Pomodoro Timer", fg=DARK_GREEN, bg=DARK_RED, font=(HANDWRITING_FONT, 20))
subheader_label.pack(pady=(0, 20))

title_label = tk.Label(text="TIMER", fg=DARK_GREEN, bg=DARK_RED, font=(FONT_NAME, 50, "bold"))
title_label.pack()

canvas = tk.Canvas(width=200, height=224, bg=DARK_RED, highlightthickness=0)
timer_text = canvas.create_text(100, 130, text="00:00", fill=DARK_GREEN, font=(FONT_NAME, 35, "bold"))
canvas.pack(pady=20)

start_button = tk.Button(text="START", command=start_timer, font=(IMPACT_FONT, 12, "bold"), fg=DARK_GREEN, bg=WHITE)
start_button.pack(side='left', padx=20)

reset_button = tk.Button(text="RESET", command=reset_timer, font=(IMPACT_FONT, 12, "bold"), fg=DARK_GREEN, bg=WHITE)
reset_button.pack(side='right', padx=20)

check_marks = tk.Label(fg=DARK_GREEN, bg=DARK_RED)
check_marks.pack(pady=20)

window.mainloop()