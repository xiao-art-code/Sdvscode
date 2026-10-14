import math
import os
import random
import time
import tkinter as tk


WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 360
SAVE_PATH = os.path.join(os.path.dirname(__file__), "meteor_dodge_best.txt")


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
        self.bullets: list[dict[str, float | str]] = []
        self.powerups: list[dict[str, float | str]] = []
        self.particles: list[dict[str, float | str]] = []
        self.elapsed = 0.0
        self.score = 0
        self.best_score = self.load_best_score()
        self.lives = 3
        self.shield_time = 0.0
        self.slow_time = 0.0
        self.invulnerable_time = 0.0
        self.fire_cooldown = 0.0
        self.spawn_timer = 0.0
        self.powerup_timer = 0.0
        self.last_frame = time.monotonic()
        self.stars = [
            (
                random.randrange(WIDTH),
                random.randrange(HEIGHT),
                random.choice((1, 1, 2, 2, 3)),
            )
            for _ in range(100)
        ]

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<FocusOut>", self.on_focus_lost)
        self.root.focus_set()
        self.draw()
        self.root.after(16, self.tick)

    def load_best_score(self) -> int:
        try:
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    value = int(f.read().strip() or "0")
                    return max(0, value)
        except OSError:
            pass
        return 0

    def save_best_score(self) -> None:
        try:
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                f.write(str(self.best_score))
        except OSError:
            pass

    def on_focus_lost(self, event: tk.Event) -> None:
        if self.state == "running":
            self.state = "paused"
            self.last_frame = time.monotonic()

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
        elif key in ("p", "escape") and self.state in ("running", "paused"):
            if self.state == "running":
                self.state = "paused"
            else:
                self.state = "running"
            self.last_frame = time.monotonic()
        elif key == "r" and self.state == "game_over":
            self.start_game()
        elif key in ("j", "k", "up") and key not in self.keys:
            self.shoot()
        self.keys.add(key)

    def on_key_release(self, event: tk.Event) -> None:
        self.keys.discard(event.keysym.lower())

    def start_game(self) -> None:
        self.state = "running"
        self.player_x = WIDTH / 2
        self.player_y = HEIGHT - 70
        self.lives = 3
        self.score = 0
        self.elapsed = 0.0
        self.meteors.clear()
        self.bullets.clear()
        self.powerups.clear()
        self.particles.clear()
        self.shield_time = 0.0
        self.slow_time = 0.0
        self.invulnerable_time = 0.0
        self.fire_cooldown = 0.0
        self.spawn_timer = 0.0
        self.powerup_timer = 0.0
        self.last_frame = time.monotonic()

    def tick(self) -> None:
        now = time.monotonic()
        dt = min(now - self.last_frame, 0.05)
        self.last_frame = now

        if self.state == "running":
            self.update_game(dt)
        self.draw()
        self.root.after(16, self.tick)

    def shoot(self) -> None:
        if self.state != "running" or self.fire_cooldown > 0:
            return
        self.fire_cooldown = 0.18
        self.bullets.append(
            {
                "x": float(self.player_x),
                "y": float(self.player_y - 22),
                "radius": 4.0,
                "vy": -620.0,
                "color": "#ffe66d",
            }
        )
        self.spawn_particles(self.player_x, self.player_y - 18, "#ffe66d", 6)

    def spawn_meteor(self) -> None:
        radius = random.randint(12, 24)
        speed = random.randint(180, 280) + min(self.elapsed * 3, 240)
        self.meteors.append(
            [
                float(random.randint(radius, WIDTH - radius)),
                float(-radius),
                float(radius),
                float(speed),
                random.choice(("#ff6b4a", "#ff9f43", "#e85d75", "#ffd166")),
            ]
        )

    def spawn_powerup(self) -> None:
        kind = random.choice(("shield", "slow"))
        radius = 10
        self.powerups.append(
            {
                "x": float(random.randint(30, WIDTH - 30)),
                "y": float(-radius),
                "radius": float(radius),
                "vy": float(120 + random.random() * 40),
                "kind": kind,
                "color": "#7ef5c7" if kind == "shield" else "#7ec6ff",
            }
        )

    def spawn_particles(self, x: float, y: float, color: str, count: int = 12) -> None:
        for _ in range(count):
            angle = random.random() * math.tau
            speed = random.uniform(30, 150)
            self.particles.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(0.3, 0.8),
                    "size": random.uniform(2, 5),
                    "color": color,
                }
            )

    def apply_powerup(self, kind: str) -> None:
        if kind == "shield":
            self.shield_time = 6.0
        elif kind == "slow":
            self.slow_time = 5.0
        self.spawn_particles(self.player_x, self.player_y, "#8ef7d6", 18)

    def update_game(self, dt: float) -> None:
        self.elapsed += dt
        self.score = int(self.elapsed * 10)
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()

        if self.shield_time > 0:
            self.shield_time = max(0.0, self.shield_time - dt)
        if self.slow_time > 0:
            self.slow_time = max(0.0, self.slow_time - dt)
        if self.invulnerable_time > 0:
            self.invulnerable_time = max(0.0, self.invulnerable_time - dt)
        if self.fire_cooldown > 0:
            self.fire_cooldown = max(0.0, self.fire_cooldown - dt)

        movement = PLAYER_SPEED * dt * (0.7 if self.slow_time > 0 else 1.0)
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
            self.spawn_meteor()

        self.powerup_timer += dt
        if self.powerup_timer >= 8.0:
            self.powerup_timer = 0.0
            if random.random() < 0.75:
                self.spawn_powerup()

        for meteor in self.meteors:
            speed_factor = 0.7 if self.slow_time > 0 else 1.0
            meteor[1] = float(meteor[1]) + float(meteor[3]) * dt * speed_factor
        self.meteors = [
            meteor
            for meteor in self.meteors
            if float(meteor[1]) - float(meteor[2]) < HEIGHT + 30
        ]

        for bullet in self.bullets:
            bullet["y"] = float(bullet["y"]) + float(bullet["vy"]) * dt
        self.bullets = [
            bullet for bullet in self.bullets if float(bullet["y"]) > -20
        ]

        for powerup in self.powerups:
            powerup["y"] = float(powerup["y"]) + float(powerup["vy"]) * dt
            if float(powerup["y"]) - float(powerup["radius"]) > HEIGHT:
                continue
            if (
                math.hypot(
                    float(powerup["x"]) - self.player_x,
                    float(powerup["y"]) - self.player_y,
                )
                < float(powerup["radius"]) + self.player_radius + 5
            ):
                self.apply_powerup(str(powerup["kind"]))
                powerup["y"] = HEIGHT + 100

        self.powerups = [
            powerup
            for powerup in self.powerups
            if float(powerup["y"]) - float(powerup["radius"]) < HEIGHT + 40
        ]

        for particle in self.particles:
            particle["x"] = float(particle["x"]) + float(particle["vx"]) * dt
            particle["y"] = float(particle["y"]) + float(particle["vy"]) * dt
            particle["life"] = float(particle["life"]) - dt
        self.particles = [particle for particle in self.particles if float(particle["life"]) > 0]

        remaining_meteors: list[list[float | str]] = []
        for meteor in self.meteors:
            x, y, radius, _, _ = meteor
            hit_by_bullet = False
            for bullet in self.bullets:
                bx = float(bullet["x"])
                by = float(bullet["y"])
                br = float(bullet["radius"])
                if math.hypot(float(x) - bx, float(y) - by) < float(radius) + br:
                    self.spawn_particles(float(x), float(y), "#ffd166", 16)
                    self.score += 5
                    hit_by_bullet = True
                    bullet["y"] = -100.0
                    break
            if hit_by_bullet:
                continue
            remaining_meteors.append(meteor)
        self.meteors = remaining_meteors
        self.bullets = [
            bullet for bullet in self.bullets if float(bullet["y"]) > -50
        ]

        for meteor in self.meteors:
            x, y, radius, _, _ = meteor
            if math.hypot(float(x) - self.player_x, float(y) - self.player_y) < (
                float(radius) + self.player_radius - 2
            ):
                if self.shield_time > 0:
                    self.shield_time = 0.0
                    self.spawn_particles(float(x), float(y), "#8ef7d6", 20)
                    self.meteors.remove(meteor)
                    break
                if self.invulnerable_time > 0:
                    continue
                self.lives -= 1
                self.invulnerable_time = 1.2
                self.spawn_particles(float(x), float(y), "#ff8a80", 24)
                self.meteors.remove(meteor)
                if self.lives <= 0:
                    self.state = "game_over"
                    self.save_best_score()
                    break
                self.player_x = WIDTH / 2
                self.player_y = HEIGHT - 70
                break

    def draw(self) -> None:
        self.canvas.delete("all")
        for x, y, size in self.stars:
            alpha = 0.36 + (x + y) % 7 * 0.08
            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#6b7aa6",
                outline="",
            )

        if self.state in ("running", "paused", "game_over"):
            self.draw_game()

        if self.state == "title":
            self.draw_message(
                "陨石躲避",
                "躲开陨石，尽可能坚持更久！",
                "← → / A D 移动   J / K / ↑ 射击   空格开始",
                f"最佳：{self.best_score}",
            )
        elif self.state == "paused":
            self.draw_message(
                "已暂停",
                "休息一下也没关系",
                "按空格继续   P 切换暂停   J / K / ↑ 射击",
                f"当前得分：{self.score}",
            )
        elif self.state == "game_over":
            self.draw_message(
                "游戏结束",
                f"最终得分：{self.score}",
                "按空格再来一局   R 重新开始   J / K / ↑ 射击",
                f"最佳：{self.best_score}",
            )

    def draw_game(self) -> None:
        score = self.score
        level = score // 100 + 1
        self.canvas.create_text(
            18,
            18,
            anchor="nw",
            text=f"得分 {score:04d}   难度 {level}   最高 {self.best_score}",
            fill="#edf4ff",
            font=("Microsoft YaHei UI", 14, "bold"),
        )

        for powerup in self.powerups:
            x = float(powerup["x"])
            y = float(powerup["y"])
            r = float(powerup["radius"])
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=str(powerup["color"]),
                outline="#ecfeff",
                width=2,
            )
            label = "S" if str(powerup["kind"]) == "shield" else "T"
            self.canvas.create_text(x, y, text=label, fill="#102030", font=("Microsoft YaHei UI", 11, "bold"))

        for bullet in self.bullets:
            x = float(bullet["x"])
            y = float(bullet["y"])
            r = float(bullet["radius"])
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=str(bullet["color"]),
                outline="#fff5bd",
                width=1,
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

        for particle in self.particles:
            self.canvas.create_oval(
                float(particle["x"]) - float(particle["size"]),
                float(particle["y"]) - float(particle["size"]),
                float(particle["x"]) + float(particle["size"]),
                float(particle["y"]) + float(particle["size"]),
                fill=str(particle["color"]),
                outline="",
            )

        x = self.player_x
        y = self.player_y
        if self.shield_time > 0:
            self.canvas.create_oval(
                x - 28,
                y - 28,
                x + 28,
                y + 28,
                outline="#7ef5c7",
                width=3,
                fill="",
            )
        if self.invulnerable_time > 0 and self.invulnerable_time % 0.16 < 0.08:
            blink = "#ffd166"
        else:
            blink = "#d5f6ff"

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
            outline=blink,
            width=2,
        )
        self.canvas.create_oval(
            x - 4, y - 4, x + 4, y + 4, fill="#ffffff", outline=""
        )

        for i in range(self.lives):
            px = WIDTH - 24 - i * 22
            self.canvas.create_text(px, 26, text="❤", fill="#ff6b6b", font=("Microsoft YaHei UI", 16, "bold"))

        if self.shield_time > 0:
            self.canvas.create_text(
                18,
                46,
                anchor="nw",
                text=f"护盾 {self.shield_time:.1f}s",
                fill="#7ef5c7",
                font=("Microsoft YaHei UI", 12, "bold"),
            )
        if self.slow_time > 0:
            self.canvas.create_text(
                18,
                70,
                anchor="nw",
                text=f"减速 {self.slow_time:.1f}s",
                fill="#7ec6ff",
                font=("Microsoft YaHei UI", 12, "bold"),
            )

    def draw_message(self, title: str, subtitle: str, hint: str, extra: str = "") -> None:
        self.canvas.create_rectangle(
            110, 170, WIDTH - 110, 430, fill="#111a32", outline="#354568", width=2
        )
        self.canvas.create_text(
            WIDTH / 2,
            230,
            text=title,
            fill="#ffffff",
            font=("Microsoft YaHei UI", 34, "bold"),
        )
        self.canvas.create_text(
            WIDTH / 2,
            290,
            text=subtitle,
            fill="#b9c7e8",
            font=("Microsoft YaHei UI", 18),
        )
        if extra:
            self.canvas.create_text(
                WIDTH / 2,
                325,
                text=extra,
                fill="#ffd166",
                font=("Microsoft YaHei UI", 16, "bold"),
            )
        self.canvas.create_text(
            WIDTH / 2,
            372,
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
