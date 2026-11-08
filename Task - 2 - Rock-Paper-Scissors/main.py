import os
import sys
import math
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


# Particle system for clash and win celebration
class Particle:
    def __init__(self, x, y, vx, vy, color, radius, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.life = life
        self.max_life = life
        self.id = None

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.35  # gravity
        self.life -= 1
        return self.life > 0


class RockPaperScissorsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors")
        self.root.geometry("920x760")
        self.root.configure(bg="#0B0F19")
        self.root.resizable(False, False)

        # center window
        self.center_window(920, 760)

        # scores and state
        self.user_score = 0
        self.computer_score = 0
        self.ties = 0
        self.rounds_played = 0
        self.win_streak = 0
        self.best_streak = 0
        self.history = []  # List of 'W', 'L', 'T'
        self.fast_mode = False
        self.game_mode = "Infinite"  # "Infinite", "Best of 3", "Best of 5"
        self.target_wins = None
        self.is_animating = False

        # choices
        self.user_choice = "Rock"
        self.computer_choice = "Rock"

        # theme colors
        self.BG = "#0B0F19"
        self.CARD_BG = "#131B2E"
        self.CARD_BORDER = "#1E293B"
        self.PLAYER_CYAN = "#06B6D4"
        self.PLAYER_GLOW = "#38BDF8"
        self.CPU_PURPLE = "#A855F7"
        self.CPU_GLOW = "#C084FC"
        self.WIN_GREEN = "#10B981"
        self.LOSE_RED = "#EF4444"
        self.TIE_AMBER = "#F59E0B"
        self.TEXT_WHITE = "#FFFFFF"
        self.TEXT_MUTED = "#94A3B8"

        # hand image cache
        self.sprite_cache = {}
        self.load_hand_sprites()

        # animation state
        self.particles = []
        self.anim_step = 0
        self.anim_beat = 0
        self.player_hand_item = None
        self.cpu_hand_item = None
        self.player_base_x = 180
        self.player_base_y = 150
        self.cpu_base_x = 680
        self.cpu_base_y = 150

        # Build UI
        self.build_ui()

        # Keyboard Bindings
        self.root.bind("<r>", lambda e: self.on_choice_click("Rock"))
        self.root.bind("<R>", lambda e: self.on_choice_click("Rock"))
        self.root.bind("<p>", lambda e: self.on_choice_click("Paper"))
        self.root.bind("<P>", lambda e: self.on_choice_click("Paper"))
        self.root.bind("<s>", lambda e: self.on_choice_click("Scissors"))
        self.root.bind("<S>", lambda e: self.on_choice_click("Scissors"))
        self.root.bind("<space>", lambda e: self.on_space_pressed())
        self.root.bind("<f>", lambda e: self.toggle_fast())
        self.root.bind("<F>", lambda e: self.toggle_fast())

        # Start Particle Loop
        self.update_particles()

    def center_window(self, width, height):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - width) // 2
        y = max(10, (sh - height) // 2 - 20)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def load_hand_sprites(self):
        # Pre-cache hand sprites at various tilt angles for 60fps rotation
        choices = ["rock", "paper", "scissors"]
        roles = [("player", True), ("cpu", False)]
        angles = range(-18, 20, 2)

        for choice in choices:
            for role, is_p in roles:
                path = f"assets/{choice}_{role}.png"
                img = Image.open(path)

                for a in angles:
                    rot = img.rotate(a, resample=Image.Resampling.BILINEAR)
                    self.sprite_cache[(choice, role, a)] = ImageTk.PhotoImage(rot)

    def get_sprite(self, choice, role, angle=0):
        # Snap to nearest cached angle
        choice = choice.lower()
        role = role.lower()
        a = int(round(angle / 2.0) * 2)
        a = max(-18, min(18, a))
        return self.sprite_cache.get((choice, role, a))

    def build_ui(self):
        # top bar
        top_bar = tk.Frame(self.root, bg=self.BG)
        top_bar.pack(fill="x", padx=30, pady=(15, 5))

        # Title
        title_box = tk.Frame(top_bar, bg=self.BG)
        title_box.pack(side="left")

        title_lbl = tk.Label(
            title_box,
            text="⚡ ROCK • PAPER • SCISSORS ⚡",
            font=("Arial", 18, "bold"),
            fg=self.TEXT_WHITE,
            bg=self.BG
        )
        title_lbl.pack(anchor="w")

        # Top Right Controls
        controls_box = tk.Frame(top_bar, bg=self.BG)
        controls_box.pack(side="right")

        self.speed_btn = tk.Button(
            controls_box,
            text="⏱️ CLASSIC (3-2-1)",
            font=("Arial", 9, "bold"),
            bg=self.CARD_BG,
            fg=self.TEXT_WHITE,
            activebackground=self.CPU_PURPLE,
            activeforeground=self.TEXT_WHITE,
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.toggle_fast
        )
        self.speed_btn.pack(side="left", padx=4)

        self.mode_btn = tk.Button(
            controls_box,
            text="🎮 MODE: INFINITE",
            font=("Arial", 9, "bold"),
            bg=self.CARD_BG,
            fg=self.TEXT_WHITE,
            activebackground="#2563EB",
            activeforeground=self.TEXT_WHITE,
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.cycle_game_mode
        )
        self.mode_btn.pack(side="left", padx=4)

        # scoreboard
        score_bar = tk.Frame(self.root, bg=self.BG)
        score_bar.pack(fill="x", padx=30, pady=(10, 5))

        # Player Card (Left)
        self.player_card = tk.Frame(
            score_bar,
            bg=self.CARD_BG,
            highlightbackground=self.PLAYER_CYAN,
            highlightthickness=2,
            padx=15,
            pady=10
        )
        self.player_card.pack(side="left", expand=True, fill="both", padx=(0, 10))

        tk.Label(
            self.player_card,
            text="👤 YOU",
            font=("Arial", 12, "bold"),
            fg=self.PLAYER_GLOW,
            bg=self.CARD_BG
        ).pack()

        self.player_score_lbl = tk.Label(
            self.player_card,
            text="0",
            font=("Arial", 36, "bold"),
            fg=self.TEXT_WHITE,
            bg=self.CARD_BG
        )
        self.player_score_lbl.pack()

        self.player_streak_lbl = tk.Label(
            self.player_card,
            text="🔥 STREAK: 0 | BEST: 0",
            font=("Arial", 9, "bold"),
            fg=self.TIE_AMBER,
            bg=self.CARD_BG
        )
        self.player_streak_lbl.pack()

        # Center VS Badge
        vs_box = tk.Frame(score_bar, bg=self.BG, padx=10)
        vs_box.pack(side="left")

        tk.Label(
            vs_box,
            text="⚡ VS ⚡",
            font=("Arial", 16, "bold"),
            fg=self.TIE_AMBER,
            bg=self.BG
        ).pack(pady=(10, 2))

        self.round_badge = tk.Label(
            vs_box,
            text="ROUND 1",
            font=("Arial", 9, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.BG
        )
        self.round_badge.pack()

        # Computer Card (Right)
        self.cpu_card = tk.Frame(
            score_bar,
            bg=self.CARD_BG,
            highlightbackground=self.CPU_PURPLE,
            highlightthickness=2,
            padx=15,
            pady=10
        )
        self.cpu_card.pack(side="right", expand=True, fill="both", padx=(10, 0))

        tk.Label(
            self.cpu_card,
            text="🤖 COMPUTER",
            font=("Arial", 12, "bold"),
            fg=self.CPU_GLOW,
            bg=self.CARD_BG
        ).pack()

        self.cpu_score_lbl = tk.Label(
            self.cpu_card,
            text="0",
            font=("Arial", 36, "bold"),
            fg=self.TEXT_WHITE,
            bg=self.CARD_BG
        )
        self.cpu_score_lbl.pack()

        self.winrate_lbl = tk.Label(
            self.cpu_card,
            text="WIN RATE: 0% (0/0)",
            font=("Arial", 9, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        self.winrate_lbl.pack()

        # arena canvas
        arena_frame = tk.Frame(
            self.root,
            bg=self.BG,
            highlightbackground="#1E293B",
            highlightthickness=2
        )
        arena_frame.pack(padx=30, pady=(8, 5))

        self.canvas_w = 860
        self.canvas_h = 280
        self.canvas = tk.Canvas(
            arena_frame,
            width=self.canvas_w,
            height=self.canvas_h,
            bg="#0E1526",
            highlightthickness=0
        )
        self.canvas.pack()

        # Draw decorative arena elements
        self.draw_arena_background()

        # Hand Canvas Items
        initial_player_sprite = self.get_sprite("rock", "player", 0)
        initial_cpu_sprite = self.get_sprite("rock", "cpu", 0)

        self.player_hand_item = self.canvas.create_image(
            self.player_base_x,
            self.player_base_y,
            image=initial_player_sprite,
            anchor="center"
        )

        self.cpu_hand_item = self.canvas.create_image(
            self.cpu_base_x,
            self.cpu_base_y,
            image=initial_cpu_sprite,
            anchor="center"
        )

        # Arena announcement text (positioned near top of arena so it never overlaps hands)
        self.arena_text_id = self.canvas.create_text(
            self.canvas_w // 2,
            48,
            text="READY TO BATTLE!",
            font=("Arial", 20, "bold"),
            fill="#FFFFFF"
        )

        # result banner
        result_box = tk.Frame(self.root, bg=self.BG)
        result_box.pack(fill="x", padx=30, pady=(6, 4))

        self.result_banner = tk.Label(
            result_box,
            text="MAKE YOUR MOVE TO START!",
            font=("Arial", 16, "bold"),
            fg=self.PLAYER_GLOW,
            bg=self.BG
        )
        self.result_banner.pack()

        self.detail_banner = tk.Label(
            result_box,
            text="Rock smashes Scissors • Paper covers Rock • Scissors cuts Paper",
            font=("Arial", 10),
            fg=self.TEXT_MUTED,
            bg=self.BG
        )
        self.detail_banner.pack()

        # move buttons
        moves_frame = tk.Frame(self.root, bg=self.BG)
        moves_frame.pack(pady=(8, 6))

        self.buttons = {}
        moves_config = [
            ("Rock", "🪨", "ROCK", "[ R ]", self.PLAYER_CYAN, "#0284C7"),
            ("Paper", "📄", "PAPER", "[ P ]", self.CPU_PURPLE, "#7E22CE"),
            ("Scissors", "✂️", "SCISSORS", "[ S ]", "#0D9488", "#0F766E"),
        ]

        for choice, icon, name, key, bg_col, hover_col in moves_config:
            card = tk.Frame(
                moves_frame,
                bg=self.CARD_BG,
                highlightbackground=bg_col,
                highlightthickness=2,
                padx=5,
                pady=5
            )
            card.pack(side="left", padx=14)

            btn = tk.Button(
                card,
                text=f"{icon}\n{name}\n{key}",
                font=("Arial", 13, "bold"),
                bg=bg_col,
                fg=self.TEXT_WHITE,
                activebackground=hover_col,
                activeforeground=self.TEXT_WHITE,
                width=11,
                height=3,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda c=choice: self.on_choice_click(c)
            )
            btn.pack()

            # Hover animations
            btn.bind("<Enter>", lambda e, b=btn, hc=hover_col: b.config(bg=hc))
            btn.bind("<Leave>", lambda e, b=btn, bc=bg_col: b.config(bg=bc))

            self.buttons[choice] = btn

        # recent history & reset
        bottom_frame = tk.Frame(self.root, bg=self.BG)
        bottom_frame.pack(fill="x", padx=30, pady=(6, 10))

        # Recent History pills
        history_box = tk.Frame(bottom_frame, bg=self.BG)
        history_box.pack(side="left")

        tk.Label(
            history_box,
            text="RECENT ROUNDS:",
            font=("Arial", 9, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.BG
        ).pack(side="left", padx=(0, 8))

        self.history_frame = tk.Frame(history_box, bg=self.BG)
        self.history_frame.pack(side="left")
        self.update_history_display()

        # Reset Game Button
        reset_btn = tk.Button(
            bottom_frame,
            text="↻ RESET ALL SCORES",
            font=("Arial", 9, "bold"),
            bg="#1E293B",
            fg=self.TEXT_WHITE,
            activebackground=self.LOSE_RED,
            activeforeground=self.TEXT_WHITE,
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self.reset_scores
        )
        reset_btn.pack(side="right")

    def draw_arena_background(self):
        # Platform glow rings for Player (left) and CPU (right)
        self.canvas.create_oval(
            60, 210, 300, 260,
            outline="#06B6D4",
            width=2,
            fill="#082F49"
        )
        self.canvas.create_oval(
            560, 210, 800, 260,
            outline="#A855F7",
            width=2,
            fill="#3B0764"
        )

        # Center clash circle
        self.canvas.create_oval(
            self.canvas_w // 2 - 65, self.canvas_h // 2 - 65,
            self.canvas_w // 2 + 65, self.canvas_h // 2 + 65,
            outline="#1E293B",
            width=2
        )
        self.canvas.create_oval(
            self.canvas_w // 2 - 35, self.canvas_h // 2 - 35,
            self.canvas_w // 2 + 35, self.canvas_h // 2 + 35,
            outline="#334155",
            width=1
        )

    def toggle_fast(self):
        self.fast_mode = not self.fast_mode
        if self.fast_mode:
            self.speed_btn.config(text="⚡ FAST (INSTANT)", fg="#FDE047")
        else:
            self.speed_btn.config(text="⏱️ CLASSIC (3-2-1)", fg=self.TEXT_WHITE)

    def cycle_game_mode(self):
        if self.game_mode == "Infinite":
            self.game_mode = "Best of 3"
            self.target_wins = 2
            self.mode_btn.config(text="🏆 BEST OF 3 (FIRST TO 2)")
        elif self.game_mode == "Best of 3":
            self.game_mode = "Best of 5"
            self.target_wins = 3
            self.mode_btn.config(text="🏆 BEST OF 5 (FIRST TO 3)")
        else:
            self.game_mode = "Infinite"
            self.target_wins = None
            self.mode_btn.config(text="🎮 MODE: INFINITE")

        self.reset_scores()

    def set_buttons_state(self, state):
        for btn in self.buttons.values():
            btn.config(state=state)

    def on_choice_click(self, choice):
        if self.is_animating:
            return
        self.user_choice = choice
        self.computer_choice = random.choice(["Rock", "Paper", "Scissors"])
        self.rounds_played += 1
        self.round_badge.config(text=f"ROUND {self.rounds_played}")

        self.start_clash_animation()

    def on_space_pressed(self):
        if not self.is_animating:
            # Random move if user hits spacebar
            quick_pick = random.choice(["Rock", "Paper", "Scissors"])
            self.on_choice_click(quick_pick)

    # animation
    def start_clash_animation(self):
        self.is_animating = True
        self.set_buttons_state("disabled")

        # Hands revert to closed fists facing each other
        p_fist = self.get_sprite("rock", "player", 0)
        c_fist = self.get_sprite("rock", "cpu", 0)
        self.canvas.itemconfig(self.player_hand_item, image=p_fist)
        self.canvas.itemconfig(self.cpu_hand_item, image=c_fist)
        self.canvas.coords(self.player_hand_item, self.player_base_x, self.player_base_y)
        self.canvas.coords(self.cpu_hand_item, self.cpu_base_x, self.cpu_base_y)

        # Clear clash banners
        self.canvas.itemconfig(self.arena_text_id, text="", fill=self.TEXT_WHITE)

        if self.fast_mode:
            self.total_beats = 1
            self.beat_duration_frames = 12
        else:
            self.total_beats = 3
            self.beat_duration_frames = 18

        self.current_beat = 0
        self.current_frame = 0
        self.run_shake_beat()

    def run_shake_beat(self):
        beat_texts = [
            ("🪨 ROCK!", "#38BDF8"),
            ("📜 PAPER!", "#C084FC"),
            ("✂️ SCISSORS!", "#34D399"),
        ]

        if self.current_frame == 0:
            text, color = beat_texts[self.current_beat % len(beat_texts)]
            self.canvas.itemconfig(self.arena_text_id, text=text, fill=color)

        # bounce hands
        progress = self.current_frame / float(self.beat_duration_frames)
        bounce = math.sin(progress * math.pi)
        y_offset = -bounce * 48
        tilt_angle = -bounce * 14

        # Update Player fist position & tilt
        p_img = self.get_sprite("rock", "player", tilt_angle)
        self.canvas.itemconfig(self.player_hand_item, image=p_img)
        self.canvas.coords(self.player_hand_item, self.player_base_x, self.player_base_y + y_offset)

        # Update CPU fist position & tilt (opposite tilt)
        c_img = self.get_sprite("rock", "cpu", -tilt_angle)
        self.canvas.itemconfig(self.cpu_hand_item, image=c_img)
        self.canvas.coords(self.cpu_hand_item, self.cpu_base_x, self.cpu_base_y + y_offset)

        self.current_frame += 1

        if self.current_frame <= self.beat_duration_frames:
            self.root.after(16, self.run_shake_beat)
        else:
            self.current_beat += 1
            self.current_frame = 0
            if self.current_beat < self.total_beats:
                self.root.after(30, self.run_shake_beat)
            else:
                self.run_reveal_shoot()

    def run_reveal_shoot(self):
        # reveal choices
        self.canvas.itemconfig(self.arena_text_id, text="💥 SHOOT!", fill="#FACC15")

        # show chosen hands
        p_revealed = self.get_sprite(self.user_choice, "player", 0)
        c_revealed = self.get_sprite(self.computer_choice, "cpu", 0)
        self.canvas.itemconfig(self.player_hand_item, image=p_revealed)
        self.canvas.itemconfig(self.cpu_hand_item, image=c_revealed)

        # punch forward
        thrust_frames = 8
        thrust_dist = 42

        def _thrust_step(f):
            t = f / float(thrust_frames)
            thrust = math.sin(t * math.pi * 0.5) * thrust_dist
            self.canvas.coords(self.player_hand_item, self.player_base_x + thrust, self.player_base_y)
            self.canvas.coords(self.cpu_hand_item, self.cpu_base_x - thrust, self.cpu_base_y)
            if f < thrust_frames:
                self.root.after(16, lambda: _thrust_step(f + 1))
            else:
                self.conclude_round()

        _thrust_step(1)

    def conclude_round(self):
        # check winner
        u = self.user_choice
        c = self.computer_choice

        if u == c:
            outcome = "TIE"
            result_text = "🤝 IT'S A TIE!"
            detail_text = f"Both chose {u}! It's a draw."
            result_color = self.TIE_AMBER
            self.ties += 1
            self.history.append("T")
            self.spawn_clash_particles(color="#FACC15", count=25)

        elif (
            (u == "Rock" and c == "Scissors") or
            (u == "Paper" and c == "Rock") or
            (u == "Scissors" and c == "Paper")
        ):
            outcome = "WIN"
            result_text = "🎉 YOU WIN!"
            result_color = self.WIN_GREEN
            self.user_score += 1
            self.win_streak += 1
            self.best_streak = max(self.best_streak, self.win_streak)
            self.history.append("W")

            if u == "Rock":
                detail_text = "Rock crushes Scissors!"
            elif u == "Paper":
                detail_text = "Paper covers Rock!"
            else:
                detail_text = "Scissors cuts Paper!"

            self.spawn_clash_particles(color="#10B981", count=45)
            self.celebrate_hand(is_player=True)

        else:
            outcome = "LOSE"
            result_text = "🤖 COMPUTER WINS!"
            result_color = self.LOSE_RED
            self.computer_score += 1
            self.win_streak = 0
            self.history.append("L")

            if c == "Rock":
                detail_text = "Computer's Rock crushes Scissors!"
            elif c == "Paper":
                detail_text = "Computer's Paper covers Rock!"
            else:
                detail_text = "Computer's Scissors cuts Paper!"

            self.spawn_clash_particles(color="#EF4444", count=35)
            self.celebrate_hand(is_player=False)

        # update result
        self.result_banner.config(text=result_text, fg=result_color)
        self.detail_banner.config(text=detail_text)
        self.canvas.itemconfig(self.arena_text_id, text=result_text, fill=result_color)

        # update score
        self.player_score_lbl.config(text=str(self.user_score))
        self.cpu_score_lbl.config(text=str(self.computer_score))
        self.player_streak_lbl.config(text=f"🔥 STREAK: {self.win_streak} | BEST: {self.best_streak}")

        total_decided = self.user_score + self.computer_score
        rate = int((self.user_score / total_decided) * 100) if total_decided > 0 else 0
        self.winrate_lbl.config(text=f"WIN RATE: {rate}% ({self.user_score}/{total_decided})")

        self.update_history_display()

        # check tournament winner
        if self.target_wins:
            if self.user_score >= self.target_wins:
                self.show_match_winner(is_player=True)
                return
            elif self.computer_score >= self.target_wins:
                self.show_match_winner(is_player=False)
                return

        # Re-enable controls
        self.is_animating = False
        self.set_buttons_state("normal")

    def celebrate_hand(self, is_player):
        # Quick victory hop
        item = self.player_hand_item if is_player else self.cpu_hand_item
        base_x = self.player_base_x + 42 if is_player else self.cpu_base_x - 42
        base_y = self.player_base_y

        def _hop(f):
            if f <= 10:
                hop_y = -abs(math.sin(f / 10.0 * math.pi)) * 25
                self.canvas.coords(item, base_x, base_y + hop_y)
                self.root.after(16, lambda: _hop(f + 1))
            else:
                self.canvas.coords(item, base_x, base_y)

        _hop(1)

    def spawn_clash_particles(self, color, count=35):
        cx = self.canvas_w // 2
        cy = self.canvas_h // 2
        palette = [color, "#FFFFFF", "#FDE047", "#67E8F9"]

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3.5, 9.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 1.5
            rad = random.randint(3, 7)
            col = random.choice(palette)
            life = random.randint(18, 36)
            p = Particle(cx, cy, vx, vy, col, rad, life)
            p.id = self.canvas.create_oval(cx - rad, cy - rad, cx + rad, cy + rad, fill=col, outline="")
            self.particles.append(p)

    def update_particles(self):
        surviving = []
        for p in self.particles:
            if p.update():
                self.canvas.coords(p.id, p.x - p.radius, p.y - p.radius, p.x + p.radius, p.y + p.radius)
                surviving.append(p)
            else:
                self.canvas.delete(p.id)
        self.particles = surviving
        self.root.after(16, self.update_particles)

    def update_history_display(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        recent = self.history[-8:]
        if not recent:
            tk.Label(
                self.history_frame,
                text="No matches yet",
                font=("Arial", 8),
                fg=self.TEXT_MUTED,
                bg=self.BG
            ).pack(side="left")
            return

        for res in recent:
            if res == "W":
                bg = self.WIN_GREEN
                txt = "W"
            elif res == "L":
                bg = self.LOSE_RED
                txt = "L"
            else:
                bg = self.TIE_AMBER
                txt = "T"

            pill = tk.Label(
                self.history_frame,
                text=txt,
                font=("Arial", 8, "bold"),
                fg=self.TEXT_WHITE,
                bg=bg,
                width=2,
                padx=2,
                pady=1
            )
            pill.pack(side="left", padx=2)

    def show_match_winner(self, is_player):
        self.is_animating = False
        if is_player:
            msg = f"🏆 MATCH VICTORY! 🎉\n\nYou won {self.user_score} - {self.computer_score} in {self.game_mode}!"
            self.spawn_clash_particles(color="#10B981", count=80)
        else:
            msg = f"🤖 COMPUTER WINS THE MATCH!\n\nFinal Score: {self.computer_score} - {self.user_score} in {self.game_mode}!"
            self.spawn_clash_particles(color="#EF4444", count=60)

        self.root.after(400, lambda: messagebox.showinfo("Match Concluded", msg))
        self.root.after(450, self.reset_scores)

    def reset_scores(self):
        self.user_score = 0
        self.computer_score = 0
        self.ties = 0
        self.rounds_played = 0
        self.win_streak = 0
        self.history.clear()

        self.player_score_lbl.config(text="0")
        self.cpu_score_lbl.config(text="0")
        self.player_streak_lbl.config(text=f"🔥 STREAK: 0 | BEST: {self.best_streak}")
        self.winrate_lbl.config(text="WIN RATE: 0% (0/0)")
        self.round_badge.config(text="ROUND 1")
        self.result_banner.config(text="SCORES RESET • READY TO PLAY!", fg=self.PLAYER_GLOW)
        self.detail_banner.config(text="Choose Rock, Paper or Scissors to begin.")

        self.canvas.itemconfig(self.arena_text_id, text="READY TO BATTLE!", fill=self.TEXT_WHITE)

        # Reset hands to base fists
        p_fist = self.get_sprite("rock", "player", 0)
        c_fist = self.get_sprite("rock", "cpu", 0)
        self.canvas.itemconfig(self.player_hand_item, image=p_fist)
        self.canvas.itemconfig(self.cpu_hand_item, image=c_fist)
        self.canvas.coords(self.player_hand_item, self.player_base_x, self.player_base_y)
        self.canvas.coords(self.cpu_hand_item, self.cpu_base_x, self.cpu_base_y)

        self.set_buttons_state("normal")
        self.is_animating = False
        self.update_history_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = RockPaperScissorsGame(root)
    root.mainloop()
