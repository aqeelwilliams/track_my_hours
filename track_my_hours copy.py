import customtkinter as ctk
from tkinter import messagebox, filedialog
import time
import csv
import threading

class TaskTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Track My Hours")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # State variables
        self.current_task = None
        self.task_start_time = 0
        self.is_timing = False
        self.recorded_tasks = []
        self.notified_interval = False

        # Task Name Entry
        self.task_name_label = ctk.CTkLabel(root, text="Input your task name:")
        self.task_name_label.pack(pady=5)

        self.task_name_entry = ctk.CTkEntry(root, width=300)
        self.task_name_entry.pack(pady=5)

        # Notification Interval Dropdown
        self.notification_interval_var = ctk.StringVar(value="30")
        interval_label = ctk.CTkLabel(root, text="Select your task reminder interval (minutes):")
        interval_label.pack(pady=5)

        interval_options = ["15", "30", "60", "Never"]
        interval_menu = ctk.CTkOptionMenu(root, variable=self.notification_interval_var, values=interval_options)
        interval_menu.pack(pady=5)

        # Buttons
        self.start_button = ctk.CTkButton(root, text="Start Task", command=self.start_task, fg_color="green")
        self.start_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(root, text="Stop Task", command=self.stop_task, state="disabled", fg_color="red")
        self.stop_button.pack(pady=5)

        self.export_button = ctk.CTkButton(root, text="Export Tasks to CSV", command=self.export_csv)
        self.export_button.pack(pady=5)

        # Elapsed Time and Current Task Label
        self.elapsed_time_label = ctk.CTkLabel(root, text="No active task", font=("Arial", 12, "bold"))
        self.elapsed_time_label.pack(pady=10)

        # Recorded Tasks Table
        self.tasks_frame = ctk.CTkFrame(root, width=500, height=200)
        self.tasks_frame.pack(pady=10, padx=10)

        self.tasks_table = ctk.CTkTextbox(self.tasks_frame, height=200, width=300)
        self.tasks_table.pack(pady=5)
        self.tasks_table.configure(state="normal")
        self.tasks_table.insert("end", f"{'Date':<25}{'Time':<20}{'Task Name':<20}\n")
        self.tasks_table.insert("end", "-" * 86 + "\n")
        self.tasks_table.configure(state="disabled")

        # Start notification thread
        self.notification_thread = threading.Thread(target=self.check_notifications, daemon=True)
        self.notification_thread.start()

        # Recurring timer update
        self.update_elapsed_time()

    def start_task(self):
        if self.is_timing:
            messagebox.showinfo("Info", "A task is already running. Stop it first.")
            return

        task_name = self.task_name_entry.get().strip()
        if not task_name:
            messagebox.showwarning("Warning", "Please enter a task name.")
            return

        self.current_task = task_name
        self.task_start_time = time.time()
        self.is_timing = True
        self.notified_interval = False
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_task(self):
        if not self.is_timing:
            return

        end_time = time.time()
        duration_seconds = end_time - self.task_start_time

        hrs = int(duration_seconds // 3600)
        mins = int((duration_seconds % 3600) // 60)
        duration_str = f"{hrs:02}:{mins:02}"

        date_str = time.strftime("%d/%m/%Y", time.localtime(self.task_start_time))

        task_info = {
            "name": self.current_task,
            "duration_str": duration_str,
            "start_timestamp": self.task_start_time,
            "end_timestamp": end_time,
            "date": date_str
        }
        self.recorded_tasks.append(task_info)

        # Update the tasks table
        self.tasks_table.configure(state="normal")
        self.tasks_table.insert("end", f"{task_info['date']:<18}{task_info['duration_str']:<20}{task_info['name']:<27}\n")
        self.tasks_table.configure(state="disabled")

        self.current_task = None
        self.is_timing = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

        messagebox.showinfo(
            "Task Stopped",
            f"Task '{task_info['name']}' recorded for {duration_str} (HH:MM)."
        )

    def export_csv(self):
        if not self.recorded_tasks:
            messagebox.showinfo("No Tasks", "No tasks recorded yet.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[["CSV files", "*.csv"]],
            title="Save Task Data As..."
        )
        if not file_path:
            return

        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Task Name", "Date", "Start Time", "End Time", "Duration (HH:MM)"])

            for t in self.recorded_tasks:
                start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t["start_timestamp"]))
                end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t["end_timestamp"]))
                writer.writerow([t["name"], t["date"], start_time_str, end_time_str, t["duration_str"]])

        messagebox.showinfo("Export Complete", f"Tasks exported to {file_path}")

    def check_notifications(self):
        check_interval = 10
        while True:
            if self.is_timing:
                user_selection = self.notification_interval_var.get()
                if user_selection != "Never":
                    notification_interval = int(user_selection) * 60
                    elapsed = time.time() - self.task_start_time
                    if elapsed >= notification_interval and not self.notified_interval:
                        self.root.after(0, self.prompt_continue_or_stop)
                        self.notified_interval = True
                    elif elapsed >= notification_interval:
                        self.notified_interval = False
            time.sleep(check_interval)

    def prompt_continue_or_stop(self):
        response = messagebox.askyesno(
            "Continue Task?",
            f"You have been working on '{self.current_task}' "
            f"for {self.notification_interval_var.get()} minutes.\n\nContinue timing?"
        )
        if not response:
            self.stop_task()

    def update_elapsed_time(self):
        if self.is_timing:
            elapsed_seconds = int(time.time() - self.task_start_time)
            hrs = elapsed_seconds // 3600
            mins = (elapsed_seconds % 3600) // 60
            secs = elapsed_seconds % 60
            self.elapsed_time_label.configure(
                text=f"Current Task: {self.current_task}\nElapsed: {hrs:02d}:{mins:02d}:{secs:02d}"
            )
        else:
            self.elapsed_time_label.configure(text="No active task")
        self.root.after(1000, self.update_elapsed_time)

def run_app():
    root = ctk.CTk()
    app = TaskTimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()