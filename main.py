import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker App")
        self.root.geometry("800x600")

        # Top Frame for Profile Info
        self.profile_frame = ttk.Frame(self.root, padding=(10, 10))
        self.profile_frame.pack(side=tk.TOP, fill=tk.X)

        self.avatar_image = Image.open("default_avatar.png")  # Placeholder for avatar
        self.avatar_image = self.avatar_image.resize((100, 100))
        self.avatar_photo = ImageTk.PhotoImage(self.avatar_image)

        self.avatar_label = ttk.Label(self.profile_frame, image=self.avatar_photo)
        self.avatar_label.pack(side=tk.LEFT, padx=(0, 20))

        self.user_info = ttk.Frame(self.profile_frame)
        self.user_info.pack(side=tk.LEFT, fill=tk.Y)

        self.username_label = ttk.Label(self.user_info, text="Username: User", font=("Arial", 14))
        self.username_label.pack(anchor="w")

        self.level_label = ttk.Label(self.user_info, text="Level: 1", font=("Arial", 14))
        self.level_label.pack(anchor="w")

        self.exp_label = ttk.Label(self.user_info, text="EXP: 0/100", font=("Arial", 14))
        self.exp_label.pack(anchor="w")

        # Middle Frame for Habit List
        self.habit_frame = ttk.Frame(self.root, padding=(10, 10))
        self.habit_frame.pack(fill=tk.BOTH, expand=True)

        self.habit_label = ttk.Label(self.habit_frame, text="Daily Habits", font=("Arial", 16))
        self.habit_label.pack(anchor="w")

        self.habit_list = ttk.Treeview(self.habit_frame, columns=("Status"), show="headings")
        self.habit_list.heading("Status", text="Status")
        self.habit_list.pack(fill=tk.BOTH, expand=True)

        # Sample Habits
        self.sample_habits = [
            ("Workout", "Not Completed"),
            ("Read a Book", "Not Completed"),
            ("Play Guitar", "Not Completed"),
            ("Code/Program", "Not Completed")
        ]
        for habit in self.sample_habits:
            self.habit_list.insert("", tk.END, values=habit)

        # Bottom Frame for Buttons
        self.button_frame = ttk.Frame(self.root, padding=(10, 10))
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.complete_task_button = ttk.Button(self.button_frame, text="Complete Task", command=self.complete_task)
        self.complete_task_button.pack(side=tk.LEFT, padx=5)

        self.add_habit_button = ttk.Button(self.button_frame, text="Add Habit", command=self.add_habit)
        self.add_habit_button.pack(side=tk.LEFT, padx=5)

        self.remove_habit_button = ttk.Button(self.button_frame, text="Remove Habit", command=self.remove_habit)
        self.remove_habit_button.pack(side=tk.LEFT, padx=5)

    def complete_task(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            current_values = self.habit_list.item(selected_item, "values")
            if current_values[1] != "Completed":
                # Mark task as completed
                self.habit_list.item(selected_item, values=(current_values[0], "Completed"))

                # Update EXP
                exp_gain = 20  # Example EXP for completing a task
                current_exp = int(self.exp_label.cget("text").split("/")[0].split(":")[1].strip())
                max_exp = int(self.exp_label.cget("text").split("/")[1])
                current_level = int(self.level_label.cget("text").split(":")[1].strip())

                new_exp = current_exp + exp_gain
                if new_exp >= max_exp:
                    # Level up
                    current_level += 1
                    new_exp -= max_exp
                    max_exp += 50  # Increment max EXP for the next level (optional)
                    self.level_label.config(text=f"Level: {current_level}")

                # Update EXP label
                self.exp_label.config(text=f"EXP: {new_exp}/{max_exp}")

    def add_habit(self):
        new_habit = "New Habit"
        self.habit_list.insert("", tk.END, values=(new_habit, "Not Completed"))

    def remove_habit(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            self.habit_list.delete(selected_item)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
