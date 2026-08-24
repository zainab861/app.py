import sqlite3
import random
import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk

DB_NAME = "aesthetic_social_app.db"
UPLOAD_FOLDER = "uploaded_images"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

CURRENT_USER = None
CURRENT_NICKNAME = None


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       anonymous_nickname
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS thoughts
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       author_nickname
                       TEXT
                       NOT
                       NULL,
                       content
                       TEXT
                       NOT
                       NULL,
                       image_path
                       TEXT,
                       timestamp
                       TEXT
                       NOT
                       NULL,
                       likes
                       INTEGER
                       DEFAULT
                       0,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS comments
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       thought_id
                       INTEGER,
                       author_nickname
                       TEXT
                       NOT
                       NULL,
                       content
                       TEXT
                       NOT
                       NULL,
                       timestamp
                       TEXT
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       thought_id
                   ) REFERENCES thoughts
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   """)

    conn.commit()
    conn.close()


def generate_nickname():
    adjectives = ["Dreamy", "Stellar", "Velvet", "Plush", "Blush", "Cotton", "Honey", "Lunar"]
    nouns = ["Bunny", "Peach", "Cloud", "Spark", "Mallow", "Paws", "Petal", "Star"]
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}"


class AestheticSocialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aesthetic Thoughts 🌸")
        self.root.geometry("650x750")
        self.root.config(bg="#fce4ec")

        init_db()
        self.photo_references = []
        self.create_widgets()

    def create_widgets(self):
        self.header_frame = tk.Frame(self.root, bg="#f8bbd0", height=40)
        self.header_frame.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="🌸 Status: Not Logged In")
        self.status_label = tk.Label(self.header_frame, textvariable=self.status_var, font=("Segoe UI", 10, "bold"),
                                     bg="#f8bbd0", fg="#880e4f")
        self.status_label.pack(pady=8)

        self.container = tk.Frame(self.root, bg="#fce4ec")
        self.container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        self.show_login_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_container()

        card = tk.Frame(self.container, bg="white", bd=0, relief=tk.FLAT)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=450)

        tk.Label(card, text="✨ Welcome Back ✨", font=("Segoe UI", 18, "bold"), bg="white", fg="#ad1457").pack(pady=25)

        tk.Label(card, text="Username", font=("Segoe UI", 10, "bold"), bg="white", fg="#616161").pack(anchor="w",
                                                                                                      padx=40)
        self.login_user_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#f5f5f5", relief=tk.FLAT, width=30)
        self.login_user_entry.pack(pady=5, ipady=4, padx=40)

        tk.Label(card, text="Password", font=("Segoe UI", 10, "bold"), bg="white", fg="#616161").pack(anchor="w",
                                                                                                      padx=40,
                                                                                                      pady=(10, 0))
        self.login_pass_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#f5f5f5", relief=tk.FLAT, width=30, show="*")
        self.login_pass_entry.pack(pady=5, ipady=4, padx=40)

        login_btn = tk.Button(card, text="Log In", font=("Segoe UI", 11, "bold"), bg="#ec407a", fg="white",
                              relief=tk.FLAT, width=22, command=self.handle_login)
        login_btn.pack(pady=20, ipady=3)

        reg_btn = tk.Button(card, text="Create a New Account", font=("Segoe UI", 9, "underline"), bg="white",
                            fg="#ad1457", bd=0, relief=tk.FLAT, command=self.show_register_screen)
        reg_btn.pack()

    def show_register_screen(self):
        self.clear_container()

        card = tk.Frame(self.container, bg="white", bd=0, relief=tk.FLAT)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=480)

        tk.Label(card, text="🌸 Create Account 🌸", font=("Segoe UI", 18, "bold"), bg="white", fg="#ad1457").pack(pady=20)

        tk.Label(card, text="Choose Username", font=("Segoe UI", 10, "bold"), bg="white", fg="#616161").pack(anchor="w",
                                                                                                             padx=40)
        self.reg_user_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#f5f5f5", relief=tk.FLAT, width=30)
        self.reg_user_entry.pack(pady=5, ipady=4, padx=40)

        tk.Label(card, text="Choose Password", font=("Segoe UI", 10, "bold"), bg="white", fg="#616161").pack(anchor="w",
                                                                                                             padx=40,
                                                                                                             pady=(10,
                                                                                                                   0))
        self.reg_pass_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#f5f5f5", relief=tk.FLAT, width=30, show="*")
        self.reg_pass_entry.pack(pady=5, ipady=4, padx=40)

        register_btn = tk.Button(card, text="Sign Up", font=("Segoe UI", 11, "bold"), bg="#ec407a", fg="white",
                                 relief=tk.FLAT, width=22, command=self.handle_register)
        register_btn.pack(pady=20, ipady=3)

        back_btn = tk.Button(card, text="Back to Log In", font=("Segoe UI", 9, "underline"), bg="white", fg="#ad1457",
                             bd=0, relief=tk.FLAT, command=self.show_login_screen)
        back_btn.pack()

    def handle_register(self):
        username = self.reg_user_entry.get().strip()
        password = self.reg_pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in both fields!")
            return

        nickname = generate_nickname()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, anonymous_nickname) VALUES (?, ?, ?)",
                           (username, password, nickname))
            conn.commit()
            messagebox.showinfo("Success!",
                                f"Account created successfully!\nYour secret identity is: {nickname}\nYou can now log in.")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "That username is already taken.")
        finally:
            conn.close()

    def handle_login(self):
        global CURRENT_USER, CURRENT_NICKNAME
        username = self.login_user_entry.get().strip()
        password = self.login_pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, anonymous_nickname FROM users WHERE username = ? AND password = ?",
                       (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            CURRENT_USER = user[0]
            CURRENT_NICKNAME = user[2]
            self.status_var.set(f"🌸 Logged in as: {CURRENT_NICKNAME}")
            self.show_main_feed()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def show_main_feed(self):
        self.clear_container()

        top_bar = tk.Frame(self.container, bg="#fce4ec")
        top_bar.pack(fill=tk.X, pady=5)

        tk.Button(top_bar, text="✍️ Write Thought", bg="#f48fb1", fg="white", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10, pady=5, command=self.open_post_window).pack(side=tk.LEFT)
        tk.Button(top_bar, text="🔄 Refresh", bg="#ce93d8", fg="white", font=("Segoe UI", 10), relief=tk.FLAT, padx=10,
                  pady=5, command=self.load_feed_data).pack(side=tk.LEFT, padx=10)
        tk.Button(top_bar, text="🔒 Logout", bg="#ef9a9a", fg="white", font=("Segoe UI", 10), relief=tk.FLAT, padx=10,
                  pady=5, command=self.logout).pack(side=tk.RIGHT)

        self.feed_area = scrolledtext.ScrolledText(self.container, wrap=tk.WORD, font=("Segoe UI", 10), bg="white",
                                                   fg="#4a148c", bd=0, relief=tk.FLAT)
        self.feed_area.pack(pady=10, fill=tk.BOTH, expand=True)
        self.feed_area.config(state=tk.DISABLED)

        action_frame = tk.Frame(self.container, bg="#f8bbd0", padx=10, pady=10)
        action_frame.pack(fill=tk.X, pady=5)

        tk.Label(action_frame, text="Thought ID:", bg="#f8bbd0", font=("Segoe UI", 9, "bold"), fg="#880e4f").pack(
            side=tk.LEFT)
        self.id_entry = tk.Entry(action_frame, font=("Segoe UI", 10), width=5, relief=tk.FLAT)
        self.id_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(action_frame, text="💖 Like", bg="#f06292", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
                  command=self.gui_like).pack(side=tk.LEFT, padx=3)
        tk.Button(action_frame, text="💬 Comment", bg="#ba68c8", fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, command=self.gui_comment).pack(side=tk.LEFT, padx=3)
        tk.Button(action_frame, text="🗑️ Delete", bg="#e57373", fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, command=self.gui_delete).pack(side=tk.LEFT, padx=3)

        self.load_feed_data()

    def load_feed_data(self):
        self.feed_area.config(state=tk.NORMAL)
        self.feed_area.delete("1.0", tk.END)
        self.photo_references.clear()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, author_nickname, content, image_path, timestamp, likes FROM thoughts ORDER BY id DESC")
        all_thoughts = cursor.fetchall()

        if not all_thoughts:
            self.feed_area.insert(tk.END, "🌸 No thoughts shared yet. Be the first one to spill your mind!")
        else:
            for row in all_thoughts:
                thought_id, author, content, img_path, timestamp, likes = row
                self.feed_area.insert(tk.END,
                                      f"📌 [Thought #{thought_id}]  🌸 {author}  •  {timestamp}  •  💖 {likes} Likes\n")
                self.feed_area.insert(tk.END, f"\"{content}\"\n")

                if img_path and os.path.exists(img_path):
                    try:
                        pil_img = Image.open(img_path)
                        max_width = 300
                        if pil_img.width > max_width:
                            w_percent = (max_width / float(pil_img.width))
                            h_size = int((float(pil_img.height) * float(w_percent)))
                            pil_img = pil_img.resize((max_width, h_size), Image.Resampling.LANCZOS)

                        tk_img = ImageTk.PhotoImage(pil_img)
                        self.photo_references.append(tk_img)

                        self.feed_area.insert(tk.END, "\n")
                        self.feed_area.image_create(tk.END, image=tk_img)
                        self.feed_area.insert(tk.END, "\n\n")
                    except Exception as e:
                        self.feed_area.insert(tk.END, f"   [Could not load image: {e}]\n")

                cursor.execute("SELECT author_nickname, content FROM comments WHERE thought_id = ?", (thought_id,))
                comments = cursor.fetchall()
                if comments:
                    self.feed_area.insert(tk.END, "   💬 Comments:\n")
                    for c_author, c_content in comments:
                        self.feed_area.insert(tk.END, f"      ▫️ {c_author}: {c_content}\n")
                else:
                    self.feed_area.insert(tk.END, "   💬 No comments yet.\n")
                self.feed_area.insert(tk.END, "—" * 55 + "\n\n")

        conn.close()
        self.feed_area.config(state=tk.DISABLED)

    def open_post_window(self):
        post_win = tk.Toplevel(self.root)
        post_win.title("Share a Thought 🌸")
        post_win.geometry("450x450")
        post_win.config(bg="#fce4ec")
        post_win.grab_set()  # Keeps focus on the posting window

        tk.Label(post_win, text=f"Posting as: {CURRENT_NICKNAME}", font=("Segoe UI", 10, "bold"), bg="#fce4ec",
                 fg="#ad1457").pack(pady=10)

        thought_input = scrolledtext.ScrolledText(post_win, wrap=tk.WORD, width=42, height=6, font=("Segoe UI", 10))
        thought_input.pack(pady=5)

        selected_image = {"path": None}
        img_label = tk.Label(post_win, text="No image attached", font=("Segoe UI", 9, "italic"), bg="#fce4ec",
                             fg="#c2185b")
        img_label.pack(pady=5)

        def attach_image():
            file_path = filedialog.askopenfilename(
                parent=post_win,
                title="Select Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
            )
            if file_path:
                try:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(UPLOAD_FOLDER, f"{int(datetime.now().timestamp())}_{filename}")
                    shutil.copy(file_path, dest_path)
                    selected_image["path"] = dest_path
                    img_label.config(text=f"✅ Attached: {filename}", fg="#2e7d32")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not attach image: {e}", parent=post_win)

        tk.Button(post_win, text="📷 Attach Image", bg="#ce93d8", fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, command=attach_image).pack(pady=5)

        def submit_post():
            text = thought_input.get("1.0", tk.END).strip()
            if not text:
                messagebox.showerror("Error", "Thought cannot be empty!", parent=post_win)
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO thoughts (user_id, author_nickname, content, image_path, timestamp, likes)
                           VALUES (?, ?, ?, ?, ?, 0)
                           """, (CURRENT_USER, CURRENT_NICKNAME, text, selected_image["path"], timestamp))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Your thought is live! ✨", parent=post_win)
            post_win.destroy()
            self.load_feed_data()

        tk.Button(post_win, text="✨ Publish Thought", bg="#ec407a", fg="white", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, command=submit_post).pack(pady=10, ipady=3)

    def gui_like(self):
        try:
            t_id = int(self.id_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid numeric Thought ID.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM thoughts WHERE id = ?", (t_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE thoughts SET likes = likes + 1 WHERE id = ?", (t_id,))
            conn.commit()
            messagebox.showinfo("Liked", f"Liked Thought #{t_id} 💖")
            self.load_feed_data()
        else:
            messagebox.showerror("Error", "Thought ID not found.")
        conn.close()

    def gui_comment(self):
        try:
            t_id = int(self.id_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid numeric Thought ID.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM thoughts WHERE id = ?", (t_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Thought ID not found.")
            conn.close()
            return
        conn.close()

        comm_win = tk.Toplevel(self.root)
        comm_win.title(f"Comment on #{t_id} 💬")
        comm_win.geometry("350x180")
        comm_win.config(bg="#fce4ec")
        comm_win.grab_set()

        tk.Label(comm_win, text="Write your sweet comment:", font=("Segoe UI", 9, "bold"), bg="#fce4ec",
                 fg="#ad1457").pack(pady=5)
        c_input = tk.Entry(comm_win, width=35, font=("Segoe UI", 10), relief=tk.FLAT)
        c_input.pack(pady=5, ipady=3)

        def save_comment():
            text = c_input.get().strip()
            if not text:
                messagebox.showerror("Error", "Comment cannot be empty.", parent=comm_win)
                return
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comments (thought_id, author_nickname, content, timestamp) VALUES (?, ?, ?, ?)",
                           (t_id, CURRENT_NICKNAME, text, timestamp))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Comment posted! 💬", parent=comm_win)
            comm_win.destroy()
            self.load_feed_data()

        tk.Button(comm_win, text="Post Comment", bg="#ba68c8", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
                  command=save_comment).pack(pady=10)

    def gui_delete(self):
        try:
            t_id = int(self.id_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid numeric Thought ID.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM thoughts WHERE id = ?", (t_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM comments WHERE thought_id = ?", (t_id,))
            cursor.execute("DELETE FROM thoughts WHERE id = ?", (t_id,))
            conn.commit()
            messagebox.showinfo("Deleted", f"Thought #{t_id} has been removed.")
            self.load_feed_data()
        else:
            messagebox.showerror("Error", "Thought ID not found.")
        conn.close()

    def logout(self):
        global CURRENT_USER, CURRENT_NICKNAME
        CURRENT_USER = None
        CURRENT_NICKNAME = None
        self.status_var.set("🌸 Status: Not Logged In")
        self.show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = AestheticSocialApp(root)
    root.mainloop()