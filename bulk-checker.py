import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, Toplevel
import threading
import requests
import csv
from concurrent.futures import ThreadPoolExecutor
import time

# Функція, що виконує HTTPS запити та повертає статус коди та URL редіректу, якщо він є
def fetch_url(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        redirect_url = response.history[-1].headers['Location'] if response.history else None
        return url, response.status_code, redirect_url
    except requests.exceptions.RequestException:
        return url, None, None

# Відкриває нове вікно і показує URL зі статус-кодом 200
def show_success_window(successful_urls):
    success_window = Toplevel(root)
    success_window.title("Successful URLs")
    text_area = scrolledtext.ScrolledText(success_window, height=15, width=50)
    text_area.pack(padx=10, pady=10)
    for url in successful_urls:
        text_area.insert(tk.END, f"{url}\n")
    text_area.configure(state='disabled')

# Функція, що керує перевіркою URL
def check_urls():
    urls = text_input.get('1.0', tk.END).strip().splitlines()
    results.clear()
    successful_urls = []

    def fetch_urls():
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(fetch_url, url): url for url in urls}
            for future in futures:
                url, status_code, redirect_url = future.result()
                results.append((url, status_code, redirect_url))

                if status_code == 200:
                    successful_urls.append(url)  # Додаємо URL до списку успішних

                display_text = f"{url}"
                if redirect_url:
                    display_text += f" → {redirect_url}"
                display_text += f" - {status_code if status_code else 'Error'}\n"

                color = 'grey'  # Default color for unknown status
                if status_code:
                    if 200 <= status_code < 300:
                        color = 'green'
                    elif status_code == 403:
                        color = 'red'
                    elif (status_code >= 400 and status_code < 500) or (status_code >= 500):
                        color = 'orange'
                    elif 100 <= status_code < 400:
                        color = 'blue'

                result_text.insert(tk.END, display_text, color)

        end_time = time.time()
        total_time = end_time - start_time
        print(f"Time taken: {total_time:.2f} seconds")

        if successful_urls:
            show_success_window(successful_urls)

    result_text.delete('1.0', tk.END)
    threading.Thread(target=fetch_urls).start()

# Функція для збереження результатів у файл CSV зі стовпцем Redirect
def save_results():
    if not results:
        messagebox.showwarning("Warning", "No results to save!")
        return
    filename = filedialog.asksaveasfilename(filetypes=[("CSV files", "*.csv")], defaultextension=".csv")
    if not filename:
        return
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['URL', 'Status Code', 'Redirect'])
        for url, status, redirect_url in results:
            redirect = redirect_url if redirect_url else "False"
            writer.writerow([url, status, redirect])
    messagebox.showinfo("Saved", "Results saved successfully.")

results = []

# Створення головного вікна програми
root = tk.Tk()
root.title("URL Checker")

# Текстове поле для вводу URL
text_input = scrolledtext.ScrolledText(root, height=10)
text_input.pack(pady=5)

# Кнопка для перевірки URL
check_button = tk.Button(root, text="Check", command=check_urls)
check_button.pack(pady=5)

# Текстове поле для відображення результатів
result_text = scrolledtext.ScrolledText(root, height=15)
result_text.pack(pady=5)

# Налаштування тегів для кольорового виводу тексту
result_text.tag_config('green', foreground='green')
result_text.tag_config('red', foreground='red')
result_text.tag_config('blue', foreground='blue')
result_text.tag_config('orange', foreground='orange')
result_text.tag_config('grey', foreground='grey')

# Кнопка для збереження результатів у файл CSV
save_button = tk.Button(root, text="Save as CSV", command=save_results)
save_button.pack(pady=5)

# Запуск Tkinter події циклу
root.mainloop()
