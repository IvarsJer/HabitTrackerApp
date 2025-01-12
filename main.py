import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from user_profile import UserProfile
from tkinter import filedialog
import json
import os
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt


class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker App")
        self.root.geometry("800x600")

        # Initialize user profile
        self.user_profile = UserProfile()
        self.data_file = "habit_tracker_data.json"

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
            self.user_info, text=f"Username: {self.user_profile.username}", font=("Arial", 14)
        )
        self.username_label.pack(anchor="w")

        self.level_label = ttk.Label(
            self.user_info, text=f"Level: {self.user_profile.level}", font=("Arial", 14)
        )
        self.level_label.pack(anchor="w")

        self.exp_label = ttk.Label(
            self.user_info, text=f"EXP: {self.user_profile.exp}/{self.user_profile.max_exp}", font=("Arial", 14)
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
            self.habit_frame, columns=("Habit", "Status", "EXP", "Streak"), show="headings"
        )
        self.habit_list.heading("Habit", text="Habit")
        self.habit_list.heading("Status", text="Status")
        self.habit_list.heading("EXP", text="EXP Value")
        self.habit_list.heading("Streak", text="Streak")
        self.habit_list.column("Habit", width=200)
        self.habit_list.column("Status", width=150)
        self.habit_list.column("EXP", width=100)
        self.habit_list.column("Streak", width=100)
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

        # Load Data
        self.load_data()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def edit_profile(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")

        tk.Label(edit_window, text="Edit Username:").pack(pady=5)
        username_entry = ttk.Entry(edit_window)
        username_entry.insert(0, self.user_profile.username)
        username_entry.pack(pady=5)

        def save_profile():
            new_username = username_entry.get().strip()
            if new_username:
                self.user_profile.username = new_username
                self.username_label.config(text=f"Username: {new_username}")
            edit_window.destroy()

        save_button = ttk.Button(edit_window, text="Save", command=save_profile)
        save_button.pack(pady=10)

    def complete_task(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            current_values = self.habit_list.item(selected_item, "values")
            if current_values[1] != "Completed":
                new_streak = int(current_values[3]) + 1
                self.habit_list.item(
                    selected_item,
                    values=(current_values[0], "Completed", current_values[2], new_streak),
                )

                habit_name = current_values[0]
                today_date = datetime.now().strftime("%Y-%m-%d")

                # Log completion dates in the data structure
                for habit in self.habit_data:
                    if habit["habit"] == habit_name:
                        if "completion_dates" not in habit:
                            habit["completion_dates"] = []
                        habit["completion_dates"].append(today_date)

                self.save_data()

                exp_gain = int(current_values[2])
                current_exp = self.user_profile.exp
                max_exp = self.user_profile.max_exp
                current_level = self.user_profile.level

                new_exp = current_exp + exp_gain
                if new_exp >= max_exp:
                    current_level += 1
                    new_exp -= max_exp
                    max_exp += 50
                    self.level_label.config(text=f"Level: {current_level}")

                self.user_profile.exp = new_exp
                self.user_profile.level = current_level
                self.user_profile.max_exp = max_exp
                self.exp_label.config(text=f"EXP: {new_exp}/{max_exp}")

    def add_habit(self):
        add_habit_window = tk.Toplevel(self.root)
        add_habit_window.title("Add Habit")

        tk.Label(add_habit_window, text="Habit Name:").pack(pady=5)
        habit_name_entry = ttk.Entry(add_habit_window)
        habit_name_entry.pack(pady=5)

        tk.Label(add_habit_window, text="EXP Value:").pack(pady=5)
        exp_value_entry = ttk.Entry(add_habit_window)
        exp_value_entry.pack(pady=5)

        def save_habit():
            habit_name = habit_name_entry.get().strip()
            try:
                exp_value = int(exp_value_entry.get().strip())
            except ValueError:
                exp_value = 10
            if habit_name:
                self.habit_list.insert("", tk.END, values=(habit_name, "Not Completed", exp_value, 0))
                self.habit_data.append(
                    {"habit": habit_name, "status": "Not Completed", "exp_value": exp_value, "streak": 0,
                     "completion_dates": []})
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
        """Generate analytics for habit completion."""
        habit_counts = {}
        for habit in self.habit_data:
            habit_name = habit["habit"]
            completion_dates = habit.get("completion_dates", [])
            habit_counts[habit_name] = len(completion_dates)

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

    def load_data(self):
        """Load the user profile and habits from a JSON file."""
        self.habit_data = []
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)

                profile = data.get("profile", {})
                self.user_profile.username = profile.get("username", "User")
                self.user_profile.level = profile.get("level", 1)
                self.user_profile.exp = profile.get("exp", 0)
                self.user_profile.max_exp = profile.get("max_exp", 100)

                self.username_label.config(text=f"Username: {self.user_profile.username}")
                self.level_label.config(text=f"Level: {self.user_profile.level}")
                self.exp_label.config(text=f"EXP: {self.user_profile.exp}/{self.user_profile.max_exp}")

                self.habit_list.delete(*self.habit_list.get_children())
                for habit in data.get("habits", []):
                    self.habit_list.insert(
                        "", tk.END,
                        values=(habit["habit"], habit["status"], habit["exp_value"], habit["streak"])
                    )
                    self.habit_data.append(habit)

    def save_data(self):
        """Save the user profile and habits to a JSON file."""
        data = {
            "profile": {
                "username": self.user_profile.username,
                "level": self.user_profile.level,
                "exp": self.user_profile.exp,
                "max_exp": self.user_profile.max_exp,
            },
            "habits": self.habit_data
        }

        with open(self.data_file, "w") as file:
            json.dump(data, file)

    def on_exit(self):
        """Save data and exit the application."""
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
