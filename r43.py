import os
import threading
import time
import requests
import tkinter as tk
from tkinter import filedialog

import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


driver = None
download_folder = os.getcwd()
batch_running = False


def log(msg):
    status_box.insert(tk.END, msg + "\n")
    status_box.see(tk.END)


def browse_folder():
    global download_folder
    folder = filedialog.askdirectory()

    if folder:
        download_folder = folder
        folder_label.config(text=folder)
        log("Download folder set: " + folder)


def focus_chrome():

    try:
        driver.switch_to.window(driver.current_window_handle)
        driver.execute_script("window.focus();")
        time.sleep(0.4)
    except:
        pass


def start_browser():

    global driver

    tag = search_entry.get().strip()

    if not tag:
        log("Enter a search tag")
        return

    url = f"https://rule34.xxx/index.php?page=post&s=list&tags={tag}"

    chrome_options = Options()

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.get(url)

    screen_width, screen_height = pyautogui.size()

    driver.set_window_position(screen_width // 2, 0)
    driver.set_window_size(screen_width // 2, screen_height)

    log("Opened search: " + tag)

    open_first_post()


def open_first_post():

    try:

        thumb = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".thumb"))
        )

        thumb.click()

        log("Opened first post")

    except:
        log("Failed to open first post")


def get_image():

    try:

        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/images/"]'))
        )

        return link.get_attribute("href")

    except:
        return None


def download_image():

    src = get_image()

    if not src:
        log("No image detected")
        return None

    try:

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": driver.current_url
        }

        r = requests.get(src, headers=headers)

        name = src.split("/")[-1].split("?")[0]

        os.makedirs(download_folder, exist_ok=True)

        path = os.path.join(download_folder, name)

        with open(path, "wb") as f:
            f.write(r.content)

        log("Saved: " + name)

        return src

    except Exception as e:
        log("Download failed: " + str(e))
        return None


def next_post(previous_image):

    try:

        focus_chrome()

        pyautogui.press("right")

        time.sleep(1)

        WebDriverWait(driver, 10).until(
            lambda d: get_image() != previous_image
        )

        log("Next post")

    except Exception as e:
        log("Next navigation issue: " + str(e))


def batch_download():

    global batch_running

    try:
        batch_size = int(batch_entry.get())
    except:
        log("Invalid batch size")
        return

    if batch_size <= 0:
        log("Enter batch size")
        return

    batch_running = True

    focus_chrome()

    log(f"Starting batch ({batch_size})")

    last_image = None

    for i in range(batch_size):

        if not batch_running:
            log("Batch stopped")
            return

        log(f"Downloading {i+1}/{batch_size}")

        last_image = download_image()

        next_post(last_image)

    batch_running = False
    log("Batch finished")


def stop_batch():

    global batch_running
    batch_running = False
    log("Stopping batch...")


# ---------- GUI ----------

root = tk.Tk()
root.title("Rule34 Downloader")
root.geometry("420x560")
root.configure(bg="#121212")


title = tk.Label(
    root,
    text="Rule34 Downloader",
    font=("Segoe UI", 16, "bold"),
    bg="#121212",
    fg="white"
)
title.pack(pady=10)


tk.Label(root, text="Search Tag", bg="#121212", fg="#aaaaaa").pack()

search_entry = tk.Entry(
    root,
    width=30,
    font=("Segoe UI", 11),
    bg="#1e1e1e",
    fg="white",
    insertbackground="white"
)
search_entry.pack(pady=6)


tk.Button(
    root,
    text="Browse Download Folder",
    command=browse_folder,
    bg="#2d2d2d",
    fg="white",
    width=22
).pack(pady=4)


folder_label = tk.Label(
    root,
    text=download_folder,
    wraplength=380,
    bg="#121212",
    fg="#888888"
)
folder_label.pack()


tk.Button(
    root,
    text="Launch Search",
    command=lambda: threading.Thread(target=start_browser).start(),
    bg="#4CAF50",
    fg="white",
    width=22
).pack(pady=10)


batch_frame = tk.Frame(root, bg="#121212")
batch_frame.pack(pady=6)


tk.Label(
    batch_frame,
    text="Batch Size",
    bg="#121212",
    fg="#ffaa00",
    font=("Segoe UI", 10, "bold")
).grid(row=0, column=0, padx=5)


batch_entry = tk.Entry(
    batch_frame,
    width=6,
    bg="#1e1e1e",
    fg="white",
    insertbackground="white",
    justify="center"
)
batch_entry.insert(0, "20")
batch_entry.grid(row=0, column=1)


controls = tk.Frame(root, bg="#121212")
controls.pack(pady=8)


tk.Button(
    controls,
    text="Download",
    width=10,
    bg="#2196F3",
    fg="white",
    command=lambda: threading.Thread(target=download_image).start()
).grid(row=0, column=0, padx=4)


tk.Button(
    controls,
    text="Start",
    width=8,
    bg="#4CAF50",
    fg="white",
    command=lambda: threading.Thread(target=batch_download).start()
).grid(row=0, column=1, padx=4)


tk.Button(
    controls,
    text="Next",
    width=8,
    bg="#2196F3",
    fg="white",
    command=lambda: threading.Thread(target=next_post).start()
).grid(row=0, column=2, padx=4)


tk.Button(
    controls,
    text="Stop",
    width=8,
    bg="#f44336",
    fg="white",
    command=stop_batch
).grid(row=0, column=3, padx=4)


status_box = tk.Text(
    root,
    height=14,
    bg="#0b0b0b",
    fg="#00ff9c",
    insertbackground="white"
)
status_box.pack(fill="both", expand=True, padx=10, pady=10)


log("Program ready")

root.mainloop()
