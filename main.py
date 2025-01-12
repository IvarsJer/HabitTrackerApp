import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from user_profile import UserProfile
from tkinter import filedialog

class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker App")
        self.root.geometry("800x600")

        # Initialize user profile
        self.user_profile = UserProfile()

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

    def complete_task(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            current_values = self.habit_list.item(selected_item, "values")
            if current_values[1] != "Completed":
                # Mark task as completed
                self.habit_list.item(selected_item, values=(current_values[0], "Completed"))

                # Update EXP
                exp_gain = 20  # Example EXP for completing a task
                current_exp = self.user_profile.exp
                max_exp = self.user_profile.max_exp
                current_level = self.user_profile.level

                new_exp = current_exp + exp_gain
                if new_exp >= max_exp:
                    # Level up
                    current_level += 1
                    new_exp -= max_exp
                    max_exp += 50  # Increment max EXP for the next level (optional)
                    self.level_label.config(text=f"Level: {current_level}")

                # Update user profile and EXP label
                self.user_profile.exp = new_exp
                self.user_profile.level = current_level
                self.user_profile.max_exp = max_exp
                self.exp_label.config(text=f"EXP: {new_exp}/{max_exp}")

    def add_habit(self):
        new_habit = "New Habit"
        self.habit_list.insert("", tk.END, values=(new_habit, "Not Completed"))

    def remove_habit(self):
        selected_item = self.habit_list.selection()
        if selected_item:
            self.habit_list.delete(selected_item)

    def edit_profile(self):
        # Create a new popup window for editing profile
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")

        # Entry to update username
        tk.Label(edit_window, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(edit_window)
        username_entry.insert(0, self.user_profile.username)
        username_entry.pack(pady=5)

        # Button to update avatar
        def change_avatar():
            file_path = filedialog.askopenfilename(
                title="Select Avatar", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if file_path:
                self.user_profile.update_avatar(file_path)
                self.update_avatar_image()

        avatar_button = ttk.Button(edit_window, text="Change Avatar", command=change_avatar)
        avatar_button.pack(pady=10)

        # Save button
        def save_profile():
            new_username = username_entry.get()
            if new_username.strip():
                self.user_profile.update_username(new_username)
                self.username_label.config(text=f"Username: {self.user_profile.username}")
            edit_window.destroy()

        save_button = ttk.Button(edit_window, text="Save", command=save_profile)
        save_button.pack(pady=20)

    def update_avatar_image(self):
        # Update avatar image in the UI
        self.avatar_image = Image.open(self.user_profile.avatar_path)
        self.avatar_image = self.avatar_image.resize((100, 100))
        self.avatar_photo = ImageTk.PhotoImage(self.avatar_image)
        self.avatar_label.config(image=self.avatar_photo)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
