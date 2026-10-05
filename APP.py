import tkinter as tk
import math


class App:
    """Главное окно: симуляция движения робота."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Симулятор робота")
        self.root.resizable(False, False)

        self.W, self.H = 600, 600
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg="white")
        self.canvas.pack()

        # Сетка для наглядности
        for i in range(0, self.W, 50):
            self.canvas.create_line(i, 0, i, self.H, fill="#eeeeee")
            self.canvas.create_line(0, i, self.W, i, fill="#eeeeee")

        # Состояние робота
        self.x, self.y = self.W // 2, self.H // 2
        self.angle = 0.0          # радианы
        self.speed = 0.0
        self.max_speed = 5.0
        self.robot_r = 15

        self.robot_body = self.canvas.create_oval(
            0, 0, 0, 0, fill="#3a7bd5", outline="#1a3d7a", width=2
        )
        self.robot_dir = self.canvas.create_line(0, 0, 0, 0, fill="red", width=3)

        # Второе окно — джойстик
        self.joystick = Joystick(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update()

    def on_close(self):
        try:
            self.joystick.win.destroy()
        except Exception:
            pass
        self.root.destroy()

    def update(self):
        vx, vy = self.joystick.get_vector()          # -1..1 в экранных координатах
        mag = math.hypot(vx, vy)
        self.speed = mag * self.max_speed
        if mag > 0.05:
            self.angle = math.atan2(vy, vx)

        if self.speed > 0.1:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

            r = self.robot_r
            self.x = max(r, min(self.W - r, self.x))
            self.y = max(r, min(self.H - r, self.y))

        self.draw()
        self.root.after(20, self.update)

    def draw(self):
        r = self.robot_r
        self.canvas.coords(self.robot_body, self.x - r, self.y - r, self.x + r, self.y + r)
        tip_x = self.x + math.cos(self.angle) * (r + 12)
        tip_y = self.y + math.sin(self.angle) * (r + 12)
        self.canvas.coords(self.robot_dir, self.x, self.y, tip_x, tip_y)


class Joystick:
    """Второе окно: виртуальный джойстик."""

    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Джойстик")
        self.win.resizable(False, False)
        self.win.geometry("+%d+%d" % (650, 100))

        size = 300
        self.canvas = tk.Canvas(self.win, width=size, height=size,
                                bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack()

        self.cx = self.cy = size / 2
        self.base_r = 110
        self.knob_r = 30
        self.max_dist = self.base_r - self.knob_r

        # Основание
        self.canvas.create_oval(
            self.cx - self.base_r, self.cy - self.base_r,
            self.cx + self.base_r, self.cy + self.base_r,
            outline="#888888", width=3, fill="#e8e8e8"
        )
        self.canvas.create_oval(self.cx - 2, self.cy - 2, self.cx + 2, self.cy + 2,
                                fill="#aaaaaa")

        # Ручка
        self.kx, self.ky = self.cx, self.cy
        self.knob = self.canvas.create_oval(
            self.kx - self.knob_r, self.ky - self.knob_r,
            self.kx + self.knob_r, self.ky + self.knob_r,
            fill="#e74c3c", outline="#a93226", width=2
        )

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    # ---- события мыши ----
    def on_press(self, e):
        self.move_knob(e.x, e.y)

    def on_drag(self, e):
        self.move_knob(e.x, e.y)

    def on_release(self, e):
        self.kx, self.ky = self.cx, self.cy
        self.canvas.coords(
            self.knob,
            self.cx - self.knob_r, self.cy - self.knob_r,
            self.cx + self.knob_r, self.cy + self.knob_r
        )

    def move_knob(self, x, y):
        dx = x - self.cx
        dy = y - self.cy
        dist = math.hypot(dx, dy)
        if dist > self.max_dist:
            dx = dx / dist * self.max_dist
            dy = dy / dist * self.max_dist
        self.kx = self.cx + dx
        self.ky = self.cy + dy
        self.canvas.coords(
            self.knob,
            self.kx - self.knob_r, self.ky - self.knob_r,
            self.kx + self.knob_r, self.ky + self.knob_r
        )

    # ---- вектор управления ----
    def get_vector(self):
        """Возвращает (vx, vy) в диапазоне [-1, 1] в координатах экрана."""
        if self.max_dist == 0:
            return 0.0, 0.0
        return (self.kx - self.cx) / self.max_dist, (self.ky - self.cy) / self.max_dist


if __name__ == "__main__":
    App().root.mainloop()