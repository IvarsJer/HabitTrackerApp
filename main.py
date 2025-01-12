import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from user_profile import UserProfile
from tkinter import filedialog, messagebox
import json
import os
from datetime import datetime
import threading
import time
import matplotlib.pyplot as plt


class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker App")
        self.root.geometry("800x600")

        # Initialize attributes
        self.user_profile = UserProfile()
        self.data_file = "habit_tracker_data.json"
        self.habit_data = []  # Initialize as an empty list to prevent threading errors

        # Initialize style for themes
        self.style = ttk.Style()

        # Top Frame for Profile Info
        self.profile_frame = ttk.Frame(self.root, padding=(10, 10))
        self.profile_frame.pack(side=tk.TOP, fill=tk.X)

        self.avatar_image = Image.open(self.user_profile.avatar_path)  # Use profile avatar
        self.avatar_image = self.avatar_image.resize((100, 100))
        self.avatar_photo = ImageTk.PhotoImage(self.avatar_image)

        self.avatar_label = ttk.Label(self.profile_frame, image=self.avatar_photo)
        self.avatar_label.pack(side=tk.LEFT, padx=(0, 20))

        self.user_info = ttk.Frame(self.profile_frame)
        self.user_info.pack(side=tk.LEFT, fill=tk.Y)

        self.username_label = ttk.Label(
            self.user_info, text="Username: Loading...", font=("Arial", 14)
        )
        self.username_label.pack(anchor="w")

        self.level_label = ttk.Label(
            self.user_info, text="Level: 0", font=("Arial", 14)
        )
        self.level_label.pack(anchor="w")

        self.exp_label = ttk.Label(
            self.user_info, text="EXP: 0/0", font=("Arial", 14)
        )
        self.exp_label.pack(anchor="w")

        # Add an Edit Profile Button
        self.edit_profile_button = ttk.Button(
            self.profile_frame, text="Edit Profile", command=self.edit_profile
        )
        self.edit_profile_button.pack(side=tk.RIGHT, padx=10)

        # Middle Frame for Habit List
        self.habit_frame = ttk.Frame(self.root, padding=(10, 10))
        self.habit_frame.pack(fill=tk.BOTH, expand=True)

        self.habit_label = ttk.Label(self.habit_frame, text="Daily Habits", font=("Arial", 16))
        self.habit_label.pack(anchor="w")

        self.habit_list = ttk.Treeview(
            self.habit_frame,
            columns=("Habit", "Status", "EXP", "Streak", "Priority", "Reminder Time"),
            show="headings"
        )
        self.habit_list.heading("Habit", text="Habit", command=lambda: self.sort_table("Habit", False))
        self.habit_list.heading("Status", text="Status", command=lambda: self.sort_table("Status", False))
        self.habit_list.heading("EXP", text="EXP Value", command=lambda: self.sort_table("EXP", False))
        self.habit_list.heading("Streak", text="Streak", command=lambda: self.sort_table("Streak", False))
        self.habit_list.heading("Priority", text="Priority", command=lambda: self.sort_table("Priority", False))
        self.habit_list.heading("Reminder Time", text="Reminder Time", command=lambda: self.sort_table("Reminder Time", False))
        self.habit_list.column("Habit", width=200)
        self.habit_list.column("Status", width=150)
        self.habit_list.column("EXP", width=100)
        self.habit_list.column("Streak", width=100)
        self.habit_list.column("Priority", width=100)
        self.habit_list.column("Reminder Time", width=150)
        self.habit_list.pack(fill=tk.BOTH, expand=True)

        # Bottom Frame for Buttons
        self.button_frame = ttk.Frame(self.root, padding=(10, 10))
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.complete_task_button = ttk.Button(
            self.button_frame, text="Complete Task", command=self.complete_task
        )
        self.complete_task_button.pack(side=tk.LEFT, padx=5)

        self.add_habit_button = ttk.Button(
            self.button_frame, text="Add Habit", command=self.add_habit
        )
        self.add_habit_button.pack(side=tk.LEFT, padx=5)

        self.remove_habit_button = ttk.Button(
            self.button_frame, text="Remove Habit", command=self.remove_habit
        )
        self.remove_habit_button.pack(side=tk.LEFT, padx=5)

        self.analytics_button = ttk.Button(
            self.button_frame, text="View Analytics", command=self.show_analytics
        )
        self.analytics_button.pack(side=tk.LEFT, padx=5)

        self.toggle_theme_button = ttk.Button(
            self.button_frame, text="Toggle Dark Mode", command=self.toggle_theme
        )
        self.toggle_theme_button.pack(side=tk.LEFT, padx=5)

        # Load data
        self.load_data()

        # Start reminder thread after data is loaded
        threading.Thread(target=self.check_reminders, daemon=True).start()

    def edit_profile(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")

        # Center the edit profile window
        self.center_window(edit_window, 300, 200)

        tk.Label(edit_window, text="Edit Username:").pack(pady=5)
        username_entry = ttk.Entry(edit_window)
        username_entry.insert(0, self.user_profile.username)
        username_entry.pack(pady=5)

        # Add option to change avatar
        def change_avatar():
            file_path = filedialog.askopenfilename(
                title="Select Avatar", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if file_path:
                self.user_profile.update_avatar(file_path)
                self.update_avatar_image()

        avatar_button = ttk.Button(edit_window, text="Change Avatar", command=change_avatar)
        avatar_button.pack(pady=10)

        def save_profile():
            new_username = username_entry.get().strip()
            if new_username:
                self.user_profile.username = new_username
                self.username_label.config(text=f"Username: {new_username}")
            edit_window.destroy()

        save_button = ttk.Button(edit_window, text="Save", command=save_profile)
        save_button.pack(pady=10)

    def update_avatar_image(self):
        self.avatar_image = Image.open(self.user_profile.avatar_path)
        self.avatar_image = self.avatar_image.resize((100, 100))
        self.avatar_photo = ImageTk.PhotoImage(self.avatar_image)
        self.avatar_label.config(image=self.avatar_photo)

    def complete_task(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            current_values = self.habit_list.item(selected_item, "values")
            if current_values[1] != "Completed":
                new_streak = int(current_values[3]) + 1
                self.habit_list.item(
                    selected_item,
                    values=(current_values[0], "Completed", current_values[2], new_streak, current_values[4], current_values[5]),
                )

                habit_name = current_values[0]
                today_date = datetime.now().strftime("%Y-%m-%d")

                for habit in self.habit_data:
                    if habit["habit"] == habit_name:
                        if "completion_dates" not in habit:
                            habit["completion_dates"] = []
                        if today_date not in habit["completion_dates"]:
                            habit["completion_dates"].append(today_date)

                        # Sort and calculate streaks
                        habit["completion_dates"].sort()
                        habit["current_streak"], habit["longest_streak"] = self.calculate_streaks(habit["completion_dates"])

                self.save_data()

    def add_habit(self):
        add_habit_window = tk.Toplevel(self.root)
        add_habit_window.title("Add Habit")

        # Center the add habit window
        self.center_window(add_habit_window, 400, 320)

        tk.Label(add_habit_window, text="Habit Name:").pack(pady=5)
        habit_name_entry = ttk.Entry(add_habit_window)
        habit_name_entry.pack(pady=5)

        tk.Label(add_habit_window, text="EXP Value:").pack(pady=5)
        exp_value_entry = ttk.Entry(add_habit_window)
        exp_value_entry.pack(pady=5)

        tk.Label(add_habit_window, text="Reminder Time (HH:MM):").pack(pady=5)
        reminder_time_entry = ttk.Entry(add_habit_window)
        reminder_time_entry.pack(pady=5)

        tk.Label(add_habit_window, text="Priority:").pack(pady=5)
        priority_var = tk.StringVar(value="Medium")  # Default priority
        priority_menu = ttk.OptionMenu(add_habit_window, priority_var, "Medium", "Low", "Medium", "High")
        priority_menu.pack(pady=5)

        def save_habit():
            habit_name = habit_name_entry.get().strip()
            try:
                exp_value = int(exp_value_entry.get().strip())
            except ValueError:
                exp_value = 10
            reminder_time = reminder_time_entry.get().strip()
            priority = priority_var.get()
            if habit_name:
                self.habit_list.insert(
                    "", tk.END,
                    values=(habit_name, "Not Completed", exp_value, 0, priority, reminder_time)
                )
                self.habit_data.append({
                    "habit": habit_name,
                    "status": "Not Completed",
                    "exp_value": exp_value,
                    "streak": 0,
                    "completion_dates": [],
                    "priority": priority,
                    "reminder_time": reminder_time,
                })
            add_habit_window.destroy()

        save_button = ttk.Button(add_habit_window, text="Save", command=save_habit)
        save_button.pack(pady=20)

    def remove_habit(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            habit_name = self.habit_list.item(selected_item, "values")[0]
            self.habit_list.delete(selected_item)

            # Remove habit from habit data
            self.habit_data = [habit for habit in self.habit_data if habit["habit"] != habit_name]

    def show_analytics(self):
        habit_counts = {}
        for habit in self.habit_data:
            habit_name = habit["habit"]
            completion_dates = habit.get("completion_dates", [])
            habit_counts[habit_name] = len(completion_dates)

        if not habit_counts:
            messagebox.showinfo("Analytics", "No data available for analytics yet.")
            return

        sorted_habits = sorted(habit_counts.items(), key=lambda x: x[1], reverse=True)

        habit_names = [habit[0] for habit in sorted_habits]
        completion_counts = [habit[1] for habit in sorted_habits]

        plt.figure(figsize=(10, 6))
        plt.bar(habit_names, completion_counts, color='skyblue')
        plt.xlabel("Habits")
        plt.ylabel("Completion Count")
        plt.title("Habit Completion Analytics")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def check_reminders(self):
        while True:
            current_time = datetime.now().strftime("%H:%M")
            for habit in self.habit_data:
                reminder_time = habit.get("reminder_time", "")
                if reminder_time == current_time and habit["status"] == "Not Completed":
                    self.show_notification(habit["habit"])
            time.sleep(60)

    def show_notification(self, habit_name):
        messagebox.showinfo("Reminder", f"Don't forget to complete your habit: {habit_name}!")

    def toggle_theme(self):
        current_theme = self.style.theme_use()

        if current_theme == "default":
            self.style.theme_use("clam")  # Switch to dark theme
            self.style.configure(".", background="#2b2b2b", foreground="#ffffff")
            self.style.configure("Treeview", background="#333333", fieldbackground="#333333", foreground="#ffffff")
            self.style.configure("TButton", background="#444444", foreground="#ffffff")
        else:
            self.style.theme_use("default")  # Switch back to light theme
            self.style.configure(".", background="#f0f0f0", foreground="#000000")
            self.style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#000000")
            self.style.configure("TButton", background="#f0f0f0", foreground="#000000")

        # Save theme preference
        self.user_profile.theme = self.style.theme_use()
        self.save_data()

    def load_data(self):
        self.habit_data = []
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)

                profile = data.get("profile", {})
                self.user_profile.username = profile.get("username", "User")
                self.user_profile.level = profile.get("level", 1)
                self.user_profile.exp = profile.get("exp", 0)
                self.user_profile.max_exp = profile.get("max_exp", 100)
                self.user_profile.theme = profile.get("theme", "default")

                self.username_label.config(text=f"Username: {self.user_profile.username}")
                self.level_label.config(text=f"Level: {self.user_profile.level}")
                self.exp_label.config(text=f"EXP: {self.user_profile.exp}/{self.user_profile.max_exp}")

                self.habit_list.delete(*self.habit_list.get_children())
                for habit in data.get("habits", []):
                    self.habit_list.insert(
                        "", tk.END,
                        values=(
                            habit["habit"], habit["status"], habit["exp_value"],
                            habit.get("current_streak", 0), habit.get("priority", "Medium"),
                            habit.get("reminder_time", "")
                        )
                    )
                    self.habit_data.append(habit)

    def save_data(self):
        data = {
            "profile": {
                "username": self.user_profile.username,
                "level": self.user_profile.level,
                "exp": self.user_profile.exp,
                "max_exp": self.user_profile.max_exp,
                "theme": self.style.theme_use(),
            },
            "habits": self.habit_data
        }

        with open(self.data_file, "w") as file:
            json.dump(data, file)

    def calculate_streaks(self, dates):
        from datetime import timedelta

        current_streak = 1
        longest_streak = 1

        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i - 1], "%Y-%m-%d")
            current_date = datetime.strptime(dates[i], "%Y-%m-%d")

            if current_date - prev_date == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return current_streak, longest_streak

    def sort_table(self, col, reverse):
        # Get data from the treeview
        data = [(self.habit_list.set(child, col), child) for child in self.habit_list.get_children('')]

        # Special sorting for Priority column
        if col == "Priority":
            priority_order = {"Low": 0, "Medium": 1, "High": 2}
            data.sort(key=lambda x: priority_order.get(x[0], 0), reverse=reverse)
        else:
            # Sort for other columns (numeric or string)
            data.sort(key=lambda x: x[0], reverse=reverse)

        # Reorder the treeview
        for index, (_, child) in enumerate(data):
            self.habit_list.move(child, '', index)

        # Reverse the sort order for next click
        self.habit_list.heading(col, command=lambda: self.sort_table(col, not reverse))

    def on_exit(self):
        self.save_data()
        self.root.destroy()

    def center_window(self, window, width, height):
        """Centers a window relative to the main application window."""
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()