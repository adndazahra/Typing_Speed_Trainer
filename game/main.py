# main.py
import time
import random
import threading
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, EXPERT_WORDS
from score_manager import save_score, show_top_scores
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# -------------------------
# Pilih level
# -------------------------
def choose_level():
    console.print("\nPilih Level Kesulitan:", style="bold cyan")
    console.print("1. Easy")
    console.print("2. Medium")
    console.print("3. Hard")
    console.print("4. Expert")

    choice = input("Masukkan pilihan (1/2/3/4): ")

    if choice == "1":
        return EASY_WORDS, "Easy"
    elif choice == "2":
        return MEDIUM_WORDS, "Medium"
    elif choice == "3":
        return HARD_WORDS, "Hard"
    elif choice == "4":
        return EXPERT_WORDS, "Expert"
    else:
        console.print("Pilihan tidak valid! Level Medium dipilih otomatis.", style="bold yellow")
        return MEDIUM_WORDS, "Medium"

# -------------------------
# Pilih durasi
# -------------------------
def choose_duration():
    console.print("\nPilih durasi permainan (detik):", style="bold cyan")
    console.print("1. 15 detik")
    console.print("2. 30 detik")
    console.print("3. 60 detik")
    console.print("4. Custom")

    choice = input("Masukkan pilihan (1/2/3/4): ")

    if choice == "1":
        return 15
    elif choice == "2":
        return 30
    elif choice == "3":
        return 60
    elif choice == "4":
        try:
            custom = int(input("Masukkan durasi custom (detik): "))
            return max(5, custom)  # minimal 5 detik
        except:
            console.print("Input tidak valid! Default 30 detik.", style="bold yellow")
            return 30
    else:
        console.print("Pilihan tidak valid! Default 30 detik.", style="bold yellow")
        return 30

# -------------------------
# Animasi GET READY!
# -------------------------
def get_ready_animation():
    colors = ["red", "green", "yellow", "magenta", "cyan"]
    for _ in range(6):
        color = random.choice(colors)
        text = Text("✨ GET READY! ✨", style=f"bold {color}")
        console.print(text, justify="center")
        time.sleep(0.3)
        console.clear()

# -------------------------
# Game utama
# -------------------------
def typing_game():
    console.print(Panel("[bold magenta]Typing Speed Trainer[/bold magenta]", expand=False))

    # Nama pemain
    name = input("Masukkan nama Anda: ")

    # Pilih level
    words, level_name = choose_level()

    # Pilih durasi
    duration = choose_duration()
    console.print(f"\nDurasi permainan: [bold green]{duration} detik[/bold green]")

    input("Tekan ENTER untuk mulai...")

    # Animasi GET READY!
    get_ready_animation()

    # Countdown 3-2-1
    console.print("Siap??", style="bold cyan")
    for i in range(3, 0, -1):
        console.print(f"[bold yellow]{i}[/bold yellow]", justify="center")
        time.sleep(1)
        console.clear()
    console.print("[bold green]Mulai!!![/bold green]\n", justify="center")

    # Variabel permainan
    score = 0
    total_chars = 0
    correct_chars = 0
    start_time = time.time()

    stop_game = threading.Event()
    user_input_lock = threading.Lock()
    input_text = [""]

    # Thread input
    def get_input():
        while not stop_game.is_set():
            text = input("> ")
            with user_input_lock:
                input_text[0] = text

    input_thread = threading.Thread(target=get_input, daemon=True)
    input_thread.start()

    # Loop utama
    while True:
        time_left = int(duration - (time.time() - start_time))
        if time_left <= 0:
            stop_game.set()
            break

        word = random.choice(words)
        console.print(f"\nSisa waktu: [bold cyan]{time_left} detik[/bold cyan]")
        console.print(f"Ketik kata ini: [bold magenta]{word}[/bold magenta]")

        # Tunggu input pemain selama sisa waktu
        start_word_time = time.time()
        while True:
            with user_input_lock:
                if input_text[0]:
                    user_word = input_text[0]
                    input_text[0] = ""  # reset
                    break
            if time.time() - start_word_time > time_left:
                user_word = ""  # jika waktu habis
                stop_game.set()
                break
            time.sleep(0.05)

        # Feedback per huruf
        text_feedback = Text()
        for i, char in enumerate(word):
            if i < len(user_word) and user_word[i] == char:
                text_feedback.append(char, style="bold green")
                correct_chars += 1
            else:
                text_feedback.append(char, style="bold red")
        console.print(text_feedback)

        total_chars += len(user_word)

        if user_word == word:
            console.print("✔ Benar!", style="bold green")
            score += 1
        else:
            console.print("✘ Salah!", style="bold red")

    # Hasil akhir
    time_spent = time.time() - start_time
    wpm = score / time_spent * 60
    accuracy = (correct_chars / total_chars) * 100 if total_chars > 0 else 0

    console.print("\n=== Waktu Habis! ===", style="bold magenta")
    console.print(f"Nama       : [bold cyan]{name}[/bold cyan]")
    console.print(f"Level      : [bold green]{level_name}[/bold green]")
    console.print(f"Kata Benar : [bold yellow]{score}[/bold yellow]")
    console.print(f"WPM        : [bold cyan]{wpm:.2f}[/bold cyan]")
    console.print(f"Akurasi    : [bold magenta]{accuracy:.2f}%[/bold magenta]")
    console.print("=======================", style="bold magenta")

    # Simpan skor & tampilkan leaderboard
    save_score(name, level_name, score, wpm, accuracy)

    data_scores = show_top_scores(level_name)
    if data_scores:
        table = Table(title=f"Leaderboard {level_name}")
        table.add_column("Nama", style="yellow")
        table.add_column("Score", style="green")
        table.add_column("WPM", style="cyan")
        table.add_column("Akurasi", style="magenta")

        for entry in data_scores:
            table.add_row(str(entry[0]), str(entry[1]), f"{entry[2]:.2f}", f"{entry[3]:.2f}%")

        console.print(table)

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    typing_game()
