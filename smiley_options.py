# =================================================================
# SMILEY OPTIONS - INTERACTIVE APP
# This script provides a GUI to choose between a Happy and Sad 
# smiley face, using manual drawing algorithms.
# =================================================================

import tkinter as tk
import time

# GLOBAL APP STATE
# session_id: Incremented on every click to cancel previous drawing loops
# drawing_active: Master toggle for drawing status
state = {
    "drawing_active": False,
    "session_id": 0
}

def plot_point(canvas, x, y, sid, color="black", delay=0.001):
    """Plots a single pixel if the session ID is still current."""
    if not state["drawing_active"] or state["session_id"] != sid:
        return False
    try:
        canvas.create_rectangle(x, y, x+1, y+1, outline=color, fill=color)
        if delay > 0:
            canvas.update()
            time.sleep(delay)
        return True
    except tk.TclError:
        state["drawing_active"] = False
        return False

def midpoint_circle(canvas, xc, yc, r, sid, color="black", delay=0.005):
    """Manual Midpoint Circle Algorithm."""
    x, y, d = 0, r, 1 - r
    
    def plot_symmetries(xc, yc, x, y):
        if not state["drawing_active"] or state["session_id"] != sid:
            return False
        points = [(xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
                  (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)]
        try:
            for px, py in points:
                if state["session_id"] == sid:
                    canvas.create_rectangle(px, py, px+1, py+1, outline=color, fill=color)
            canvas.update()
            if delay > 0: time.sleep(delay)
            return True
        except tk.TclError:
            return False

    if not plot_symmetries(xc, yc, x, y): return
    
    while x < y and state["drawing_active"] and state["session_id"] == sid:
        x += 1
        if d < 0: d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
        if not plot_symmetries(xc, yc, x, y): break

def bresenham_line(canvas, x1, y1, x2, y2, sid, color="black", delay=0.01):
    """
    Generalized Bresenham's Line Drawing Algorithm (handles all 8 octants).
    
    Includes a 'sid' (Session ID) check to ensure that if a user clicks 
    a new button, the old line-drawing loop terminates.
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    
    x, y = x1, y1
    
    if dx > dy:
        # Case for slope |m| < 1
        p = 2 * dy - dx
        while True:
            if not state["drawing_active"] or state["session_id"] != sid: break
            if not plot_point(canvas, x, y, sid, color, delay): break
            if x == x2: break
            x += sx
            if p >= 0:
                y += sy
                p += 2 * (dy - dx)
            else:
                p += 2 * dy
    else:
        # Case for slope |m| >= 1
        p = 2 * dx - dy
        while True:
            if not state["drawing_active"] or state["session_id"] != sid: break
            if not plot_point(canvas, x, y, sid, color, delay): break
            if y == y2: break
            y += sy
            if p >= 0:
                x += sx
                p += 2 * (dx - dy)
            else:
                p += 2 * dx

def perform_drawing(canvas, label, mood):
    """
    Main orchestration function for drawing the smiley.
    Terminates existing sessions and starts a new one.
    """
    # Stop previous session and start new one
    state["session_id"] += 1
    sid = state["session_id"]
    state["drawing_active"] = True
    
    canvas.delete("all")
    label.config(text=f"Drawing {mood} Smiley...")
    
    # 1. Draw Head (Yellow)
    midpoint_circle(canvas, 250, 250, 150, sid, color="#f1c40f", delay=0.002)
    
    # 2. Draw Eyes (Blue)
    if state["session_id"] == sid:
        midpoint_circle(canvas, 190, 200, 20, sid, color="#3498db", delay=0.01)
    if state["session_id"] == sid:
        midpoint_circle(canvas, 310, 200, 20, sid, color="#3498db", delay=0.01)
        
    # 3. Draw Mouth (Dynamic based on mood)
    if state["session_id"] == sid:
        if mood == "Happy":
            # Points for a smile curve
            smile_points = [(180, 320), (210, 350), (250, 360), (290, 350), (320, 320)]
            color = "#e74c3c" # Red
        else:
            # Points for a frown curve
            smile_points = [(180, 360), (210, 330), (250, 320), (290, 330), (320, 360)]
            color = "#95a5a6" # Grey (Sad)
            
        for i in range(len(smile_points) - 1):
            if state["session_id"] != sid: break
            bresenham_line(canvas, smile_points[i][0], smile_points[i][1], 
                           smile_points[i+1][0], smile_points[i+1][1], sid, color, 0.005)
    
    if state["session_id"] == sid:
        label.config(text=f"{mood} Smiley complete!")

def on_close(root):
    state["drawing_active"] = False
    state["session_id"] += 1
    root.destroy()

def create_styled_button(parent, text, color, hover_color, command):
    """Creates a realistic 3D button with hover effects."""
    btn = tk.Button(
        parent, text=text, command=command,
        width=15, bg=color, fg="white",
        font=("Arial", 11, "bold"),
        relief="raised", borderwidth=4,
        padx=10, pady=5,
        cursor="hand2", activebackground=hover_color, activeforeground="white"
    )
    
    def on_enter(e): btn.config(bg=hover_color)
    def on_leave(e): btn.config(bg=color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def main():
    root = tk.Tk()
    root.title("Smiley Options - Choose Your Mood")
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    
    # UI Layout
    top_frame = tk.Frame(root, bg="#34495e", padx=20, pady=20)
    top_frame.pack(fill="x")
    
    canvas = tk.Canvas(root, width=500, height=500, bg="#2c3e50", highlightthickness=0)
    canvas.pack(pady=10)
    
    status_label = tk.Label(root, text="Select an option to start drawing", 
                            font=("Helvetica", 12, "italic"), fg="#ecf0f1", bg="#2c3e50")
    status_label.pack(fill="x", pady=10)
    root.config(bg="#2c3e50")
    
    btn_happy = create_styled_button(top_frame, "Happy Smiley", "#27ae60", "#2ecc71", 
                                     lambda: perform_drawing(canvas, status_label, "Happy"))
    btn_happy.pack(side="left", padx=10)
    
    btn_sad = create_styled_button(top_frame, "Sad Smiley", "#c0392b", "#e74c3c", 
                                   lambda: perform_drawing(canvas, status_label, "Sad"))
    btn_sad.pack(side="left", padx=10)
    
    root.mainloop()


if __name__ == "__main__":
    main()
