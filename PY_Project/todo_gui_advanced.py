import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json, os

DATA_FILE = "tasks.json"

@dataclass
class Task:
    title: str
    completed: bool = False
    priority: int = 1
    due_date: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Advanced To-Do List")
        self.root.geometry("700x500")
        self.tasks = self.load_tasks()
        self.build_ui()
        self.refresh_task_list()

    def load_tasks(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)
                    return [Task(**item) for item in data]
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
        return []

    def save_tasks(self):
        try:
            with open(DATA_FILE, 'w') as file:
                json.dump([asdict(task) for task in self.tasks], file, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def build_ui(self):
        ttk.Style().configure("Treeview", font=("Arial", 11), rowheight=30)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        self.task_entry = tk.Entry(frame, width=40, font=("Arial", 12))
        self.task_entry.grid(row=0, column=0, padx=5)

        self.priority = tk.IntVar(value=1)
        tk.Label(frame, text="Priority:").grid(row=0, column=1)
        tk.Spinbox(frame, from_=1, to=5, width=5, textvariable=self.priority).grid(row=0, column=2)

        self.due_date_entry = tk.Entry(frame, width=15)
        self.due_date_entry.insert(0, "YYYY-MM-DD")
        self.due_date_entry.grid(row=0, column=3, padx=5)

        tk.Button(frame, text="➕ Add Task", command=self.add_task, bg="#4CAF50", fg="white").grid(row=0, column=4, padx=5)

        self.tree = ttk.Treeview(self.root, columns=("Title", "Status", "Priority", "Due Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, fill="both", expand=True)

        self.tree.tag_configure("done", background="#c8e6c9")
        self.tree.tag_configure("pending", background="#ffcdd2")

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="✔ Mark Completed", command=self.mark_completed, bg="#2196F3", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(action_frame, text="🗑 Delete", command=self.delete_task, bg="#f44336", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(action_frame, text="⬇ Export JSON", command=self.export_json).grid(row=0, column=2, padx=5)
        tk.Button(action_frame, text="⬇ Export CSV", command=self.export_csv).grid(row=0, column=3, padx=5)

    def refresh_task_list(self):
        self.tree.delete(*self.tree.get_children())
        for i, task in enumerate(sorted(self.tasks, key=lambda x: (x.completed, x.priority))):
            status = "✔" if task.completed else "❌"
            tag = "done" if task.completed else "pending"
            self.tree.insert("", "end", iid=i, values=(task.title, status, task.priority, task.due_date), tags=(tag,))

    def add_task(self):
        title = self.task_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        if not title:
            return messagebox.showwarning("Input Error", "Task title cannot be empty")
        self.tasks.append(Task(title=title, priority=self.priority.get(), due_date=due_date))
        self.task_entry.delete(0, tk.END)
        self.refresh_task_list()
        self.save_tasks()

    def mark_completed(self):
        for sel in self.tree.selection():
            self.tasks[int(sel)].completed = True
        self.refresh_task_list()
        self.save_tasks()

    def delete_task(self):
        for sel in reversed(self.tree.selection()):
            del self.tasks[int(sel)]
        self.refresh_task_list()
        self.save_tasks()

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if path:
            json.dump([asdict(t) for t in self.tasks], open(path, 'w'), indent=4)
            messagebox.showinfo("Exported", f"Tasks exported to {path}")

    def export_csv(self):
        import csv
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "Completed", "Priority", "Due Date", "Created At"])
                for t in self.tasks:
                    writer.writerow([t.title, t.completed, t.priority, t.due_date, t.created_at])
            messagebox.showinfo("Exported", f"Tasks exported to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()