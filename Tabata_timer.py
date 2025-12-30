import tkinter as tk  # Импорт библиотеки Tkinter для GUI
from tkinter import messagebox  # Для всплывающих сообщений об ошибках
import time  # Для работы со временем
import winsound  # Для воспроизведения звуков

# ---------- Глобальные переменные ----------
running = False  # Флаг работы таймера
start_time = 0  # Время старта таймера
elapsed = 0  # Прошедшее время для секундомера
countdown_time = 0  # Введённое время для обратного отсчёта
remaining_time = 0  # Оставшееся время таймера
blink = False  # Для мигания Tabata последних секунд

tabata_mode = False  # Флаг режима Tabata
current_round = 0  # Текущий раунд Tabata
is_work = True  # Фаза работы/отдыха Tabata

work_time = 20  # Время работы Tabata по умолчанию
rest_time = 10  # Время отдыха Tabata по умолчанию
total_rounds = 8  # Количество раундов Tabata по умолчанию

laps = []  # Список кругов для секундомера и таймера

current_mode = None  # Текущий режим: 'stopwatch', 'countdown', 'tabata'

# ---------- Функции звука ----------
def beep(freq=1000, dur=200):
    """
    Воспроизводит звук заданной частоты и длительности
    freq - частота звука (Гц)
    dur - длительность (мс)
    """
    winsound.Beep(freq, dur)

# ---------- Форматирование времени ----------
def format_stopwatch(seconds):
    """
    Форматирует время для секундомера в формате MM:SS.s
    """
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:04.1f}"

def format_countdown(seconds):
    """
    Форматирует время для обратного отсчета в формат ЧЧ:ММ:СС, ММ:СС или С
    """
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    elif m > 0:
        return f"{m}:{s:02d}"
    else:
        return f"{s}"

# ---------- Сброс всех состояний ----------
def reset_all():
    """
    Сбрасывает все таймеры, состояния и списки кругов
    Вызывается при возврате в главное меню или начале нового режима
    """
    global running, elapsed, countdown_time, remaining_time, blink
    global tabata_mode, current_round, is_work, laps

    running = False
    elapsed = 0
    countdown_time = 0
    remaining_time = 0
    blink = False

    tabata_mode = False
    current_round = 0
    is_work = True

    laps.clear()

    # Сброс всех Label
    time_label_stopwatch.config(text="0", fg="black")
    time_label_countdown.config(text="0", fg="black")
    time_label_tabata.config(text="0", fg="black")
    mode_label.config(text="")
    lap_box_stopwatch.delete(0, tk.END)
    lap_box_countdown.delete(0, tk.END)

# ---------- Главное меню ----------
def show_main_menu():
    """
    Показывает главное меню и скрывает все режимы
    """
    global current_mode
    current_mode = None  # Сброс текущего режима
    stopwatch_frame.pack_forget()  # Скрываем фрейм секундомера
    countdown_frame.pack_forget()  # Скрываем фрейм обратного отсчета
    tabata_frame.pack_forget()     # Скрываем фрейм Tabata
    main_menu_frame.pack(pady=50)  # Показываем главное меню
    reset_all()  # Сбрасываем все таймеры и состояния

# ---------- Показывает выбранный фрейм ----------
def show_frame(frame, mode):
    """
    Скрывает все фреймы и показывает только выбранный
    frame - фрейм для отображения
    mode - текущий режим ('stopwatch', 'countdown', 'tabata')
    """
    global current_mode
    current_mode = mode  # Устанавливаем текущий режим
    main_menu_frame.pack_forget()
    stopwatch_frame.pack_forget()
    countdown_frame.pack_forget()
    tabata_frame.pack_forget()
    frame.pack(pady=20)  # Показываем выбранный фрейм
    reset_all()  # Сбрасываем все таймеры при переключении

# ---------- Секундомер ----------
def start_stopwatch():
    """
    Запускает секундомер
    """
    global running, start_time
    running = True
    start_time = time.time() - elapsed  # Учитываем уже прошедшее время

def pause_stopwatch():
    """
    Пауза секундомера
    """
    global running, elapsed
    if running:
        running = False
        elapsed = time.time() - start_time

def reset_stopwatch():
    """
    Сброс секундомера
    """
    global running, elapsed
    running = False
    elapsed = 0
    time_label_stopwatch.config(text="0")
    lap_box_stopwatch.delete(0, tk.END)

def lap_stopwatch():
    """
    Засекает круг секундомера
    """
    if running:
        laps.append(elapsed)
        lap_box_stopwatch.insert(tk.END, f"Круг {len(laps)}: {format_stopwatch(elapsed)}")
        beep(900, 100)  # Звук при фиксации круга

# ---------- Обратный отсчет ----------
def start_countdown():
    """
    Запускает обратный отсчет с введенного времени
    """
    global running, start_time, countdown_time, remaining_time
    try:
        seconds = int(entry_countdown.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите число секунд")
        return
    countdown_time = seconds
    remaining_time = countdown_time
    running = True
    start_time = time.time()

def pause_countdown():
    """
    Пауза обратного отсчета
    """
    global running, remaining_time, start_time, countdown_time
    if running:
        running = False
        countdown_time = remaining_time

def lap_countdown():
    """
    Засекает круг обратного отсчета
    """
    if running:
        laps.append(remaining_time)
        lap_box_countdown.insert(tk.END, f"Круг {len(laps)}: {format_countdown(remaining_time)}")
        beep(900, 100)

# ---------- Tabata ----------
def start_tabata():
    """
    Запускает Tabata с настройками работы, отдыха и количества раундов
    """
    global tabata_mode, current_round, is_work, countdown_time
    global work_time, rest_time, total_rounds, start_time, running
    try:
        work_time = int(work_entry.get())
        rest_time = int(rest_entry.get())
        total_rounds = int(rounds_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите числа")
        return
    reset_all()
    tabata_mode = True
    current_round = 1
    is_work = True
    countdown_time = work_time
    running = True
    start_time = time.time()
    mode_label.config(text=f"РАБОТА • Раунд {current_round}")
    time_label_tabata.config(fg="red")

def switch_tabata_phase():
    """
    Переключает фазу Tabata между WORK и REST
    """
    global is_work, countdown_time, current_round, running, start_time
    beep(1500 if is_work else 800, 300)
    if is_work:
        is_work = False
        countdown_time = rest_time
        mode_label.config(text=f"ОТДЫХ • Раунд {current_round}")
        time_label_tabata.config(fg="green")
    else:
        current_round += 1
        if current_round > total_rounds:
            running = False
            beep(2000, 600)
            time_label_tabata.config(fg="black")
            messagebox.showinfo("Готово", "Tabata завершена!")
            return
        is_work = True
        countdown_time = work_time
        mode_label.config(text=f"РАБОТА • Раунд {current_round}")
        time_label_tabata.config(fg="red")
    start_time = time.time()
    running = True

# ---------- Обновление таймеров ----------
def update_timer():
    """
    Постоянное обновление всех таймеров через after()
    В зависимости от текущего режима обновляет соответствующий Label
    """
    global elapsed, remaining_time, running, blink
    if running:
        current = time.time() - start_time
        if current_mode == 'stopwatch':
            elapsed = current
            time_label_stopwatch.config(text=format_stopwatch(elapsed))
        elif current_mode == 'countdown':
            remaining_time = countdown_time - current
            if remaining_time <= 0:
                running = False
                time_label_countdown.config(text="0")
                beep(1500, 400)
            else:
                time_label_countdown.config(text=format_countdown(remaining_time))
        elif current_mode == 'tabata':
            remaining_time = countdown_time - current
            if 0 < remaining_time <= 3:
                blink = not blink
                if blink:
                    time_label_tabata.config(fg="yellow")
                else:
                    time_label_tabata.config(fg="red" if is_work else "green")
                beep(2000, 100)
            else:
                time_label_tabata.config(fg="red" if is_work else "green")
            if remaining_time <= 0:
                running = False
                switch_tabata_phase()
            else:
                time_label_tabata.config(text=format_countdown(remaining_time))
    root.after(200, update_timer)

# ---------- GUI ----------
root = tk.Tk()
root.title("Умный Таймер")  # Заголовок окна

# ---------- Главное меню ----------
main_menu_frame = tk.Frame(root)
main_menu_frame.pack(pady=50)
tk.Label(main_menu_frame, text="Выберите режим:", font=("Arial", 16)).pack(pady=10)
tk.Button(main_menu_frame, text="Секундомер", width=25, command=lambda: show_frame(stopwatch_frame,'stopwatch')).pack(pady=5)
tk.Button(main_menu_frame, text="Обратный отсчет", width=25, command=lambda: show_frame(countdown_frame,'countdown')).pack(pady=5)
tk.Button(main_menu_frame, text="Tabata", width=25, command=lambda: show_frame(tabata_frame,'tabata')).pack(pady=5)

# ---------- Секундомер ----------
stopwatch_frame = tk.Frame(root)
time_label_stopwatch = tk.Label(stopwatch_frame, text="0", font=("Arial", 40))
time_label_stopwatch.pack(pady=5)
frame_buttons_stopwatch = tk.Frame(stopwatch_frame)
frame_buttons_stopwatch.pack()
tk.Button(frame_buttons_stopwatch, text="Старт", width=10, command=start_stopwatch).pack(side="left", padx=5)
tk.Button(frame_buttons_stopwatch, text="Пауза", width=10, command=pause_stopwatch).pack(side="left", padx=5)
tk.Button(frame_buttons_stopwatch, text="Сброс", width=10, command=reset_stopwatch).pack(side="left", padx=5)
tk.Button(frame_buttons_stopwatch, text="Круг", width=10, command=lap_stopwatch).pack(side="left", padx=5)
tk.Button(frame_buttons_stopwatch, text="Главное меню", width=15, command=show_main_menu).pack(side="left", padx=10)
lap_box_stopwatch = tk.Listbox(stopwatch_frame, width=35)
lap_box_stopwatch.pack(pady=5)

# ---------- Обратный отсчет ----------
countdown_frame = tk.Frame(root)
time_label_countdown = tk.Label(countdown_frame, text="0", font=("Arial", 40))
time_label_countdown.pack(pady=5)
entry_countdown = tk.Entry(countdown_frame, width=10)
entry_countdown.pack(pady=5)
frame_buttons_countdown = tk.Frame(countdown_frame)
frame_buttons_countdown.pack()
tk.Button(frame_buttons_countdown, text="Старт", width=10, command=start_countdown).pack(side="left", padx=5)
tk.Button(frame_buttons_countdown, text="Пауза", width=10, command=pause_countdown).pack(side="left", padx=5)
tk.Button(frame_buttons_countdown, text="Круг", width=10, command=lap_countdown).pack(side="left", padx=5)
tk.Button(frame_buttons_countdown, text="Главное меню", width=15, command=show_main_menu).pack(side="left", padx=10)
lap_box_countdown = tk.Listbox(countdown_frame, width=35)
lap_box_countdown.pack(pady=5)

# ---------- Tabata ----------
tabata_frame = tk.Frame(root)
time_label_tabata = tk.Label(tabata_frame, text="0", font=("Arial", 40))
time_label_tabata.pack(pady=5)
mode_label = tk.Label(tabata_frame, text="", font=("Arial", 14))
mode_label.pack()
settings = tk.Frame(tabata_frame)
settings.pack(pady=5)
tk.Label(settings, text="Время работы").grid(row=0, column=0)
work_entry = tk.Entry(settings, width=5)
work_entry.insert(0, "20")
work_entry.grid(row=0, column=1)
tk.Label(settings, text="Время отдыха").grid(row=0, column=2)
rest_entry = tk.Entry(settings, width=5)
rest_entry.insert(0, "10")
rest_entry.grid(row=0, column=3)
tk.Label(settings, text="Раунды").grid(row=0, column=4)
rounds_entry = tk.Entry(settings, width=5)
rounds_entry.insert(0, "8")
rounds_entry.grid(row=0, column=5)
frame_buttons_tabata = tk.Frame(tabata_frame)
frame_buttons_tabata.pack(pady=5)
tk.Button(frame_buttons_tabata, text="Старт Tabata", width=15, command=start_tabata).pack(side="left", padx=5)
tk.Button(frame_buttons_tabata, text="Главное меню", width=15, command=show_main_menu).pack(side="left", padx=5)

# ---------- Запуск обновления таймера ----------
update_timer()
root.mainloop()
