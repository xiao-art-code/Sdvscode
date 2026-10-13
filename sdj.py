import math
import random
import time
import tkinter as tk


WIDTH = 800
HEIGHT = 600


class MeteorDodge:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("陨石躲避 - Meteor Dodge")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg="#0b1020", highlightthickness=0
        )
        self.canvas.pack()

        self.state = "title"
        self.keys: set[str] = set()
        self.player_x = WIDTH / 2
        self.player_y = HEIGHT - 70
        self.player_radius = 18
        self.meteors: list[list[float | str]] = []
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.last_frame = time.monotonic()
        self.stars = [
            (random.randrange(WIDTH), random.randrange(HEIGHT), random.choice((1, 1, 2)))
            for _ in range(85)
        ]

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.focus_set()
        self.draw()
        self.root.after(16, self.tick)

    def on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key == "space" and key not in self.keys:
            if self.state in ("title", "game_over"):
                self.start_game()
            elif self.state == "running":
                self.state = "paused"
            elif self.state == "paused":
                self.state = "running"
            self.last_frame = time.monotonic()
        self.keys.add(key)

    def on_key_release(self, event: tk.Event) -> None:
        self.keys.discard(event.keysym.lower())

    def start_game(self) -> None:
        self.state = "running"
        self.player_x = WIDTH / 2
        self.meteors.clear()
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.last_frame = time.monotonic()

    def tick(self) -> None:
        now = time.monotonic()
        dt = min(now - self.last_frame, 0.05)
        self.last_frame = now

        if self.state == "running":
            self.update_game(dt)
        self.draw()
        self.root.after(16, self.tick)

    def update_game(self, dt: float) -> None:
        self.elapsed += dt
        movement = 360 * dt
        if "left" in self.keys or "a" in self.keys:
            self.player_x -= movement
        if "right" in self.keys or "d" in self.keys:
            self.player_x += movement
        self.player_x = max(
            self.player_radius, min(WIDTH - self.player_radius, self.player_x)
        )

        self.spawn_timer += dt
        spawn_interval = max(0.18, 0.72 - self.elapsed * 0.006)
        while self.spawn_timer >= spawn_interval:
            self.spawn_timer -= spawn_interval
            radius = random.randint(12, 24)
            self.meteors.append(
                [
                    float(random.randint(radius, WIDTH - radius)),
                    float(-radius),
                    float(radius),
                    float(random.randint(180, 280) + min(self.elapsed * 3, 240)),
                    random.choice(("#ff6b4a", "#ff9f43", "#e85d75", "#ffd166")),
                ]
            )

        for meteor in self.meteors:
            meteor[1] = float(meteor[1]) + float(meteor[3]) * dt
        self.meteors = [
            meteor
            for meteor in self.meteors
            if float(meteor[1]) - float(meteor[2]) < HEIGHT
        ]

        for x, y, radius, _, _ in self.meteors:
            if math.hypot(float(x) - self.player_x, float(y) - self.player_y) < (
                float(radius) + self.player_radius - 3
            ):
                self.state = "game_over"
                break

    def draw(self) -> None:
        self.canvas.delete("all")
        for x, y, size in self.stars:
            self.canvas.create_oval(
                x, y, x + size, y + size, fill="#526080", outline=""
            )

        if self.state in ("running", "paused", "game_over"):
            self.draw_game()

        if self.state == "title":
            self.draw_message(
                "陨石躲避",
                "躲开陨石，尽可能坚持更久！",
                "← → / A D 移动    空格开始",
            )
        elif self.state == "paused":
            self.draw_message("已暂停", "休息一下也没关系", "按空格继续")
        elif self.state == "game_over":
            self.draw_message(
                "游戏结束",
                f"最终得分：{int(self.elapsed * 10)}",
                "按空格再来一局",
            )

    def draw_game(self) -> None:
        score = int(self.elapsed * 10)
        level = score // 100 + 1
        self.canvas.create_text(
            20,
            18,
            anchor="nw",
            text=f"得分  {score:04d}      难度  {level}",
            fill="#e7ecff",
            font=("Microsoft YaHei UI", 15, "bold"),
        )

        for x, y, radius, _, color in self.meteors:
            r = float(radius)
            self.canvas.create_oval(
                float(x) - r,
                float(y) - r,
                float(x) + r,
                float(y) + r,
                fill=str(color),
                outline="#ffd3a1",
                width=2,
            )
            self.canvas.create_oval(
                float(x) - r * 0.35,
                float(y) - r * 0.4,
                float(x) + r * 0.2,
                float(y) + r * 0.15,
                fill="#ffe0a8",
                outline="",
            )

        x = self.player_x
        y = self.player_y
        self.canvas.create_polygon(
            x,
            y - 22,
            x - 17,
            y + 16,
            x,
            y + 9,
            x + 17,
            y + 16,
            fill="#62d6ff",
            outline="#d5f6ff",
            width=2,
        )
        self.canvas.create_oval(
            x - 4, y - 4, x + 4, y + 4, fill="#ffffff", outline=""
        )

    def draw_message(self, title: str, subtitle: str, hint: str) -> None:
        self.canvas.create_rectangle(
            110, 190, WIDTH - 110, 410, fill="#111a32", outline="#354568", width=2
        )
        self.canvas.create_text(
            WIDTH / 2,
            245,
            text=title,
            fill="#ffffff",
            font=("Microsoft YaHei UI", 34, "bold"),
        )
        self.canvas.create_text(
            WIDTH / 2,
            305,
            text=subtitle,
            fill="#b9c7e8",
            font=("Microsoft YaHei UI", 16),
        )
        self.canvas.create_text(
            WIDTH / 2,
            360,
            text=hint,
            fill="#73dcff",
            font=("Microsoft YaHei UI", 14),
        )


def main() -> None:
    root = tk.Tk()
    MeteorDodge(root)
    root.mainloop()


if __name__ == "__main__":
    main()
