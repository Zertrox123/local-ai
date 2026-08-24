import customtkinter as ctk
from agent_manager import *
import threading

thing = ''

app = ctk.CTk()
app.geometry("600x900")
app.title("OM_AI")


txt = "Hello there !"
count = 0
text = ''

label = ctk.CTkLabel(app,
    text=txt,
    font= ('Arial', 30),
    text_color="White")
label.pack(pady=100)

# C'est toutes les fonctions

def slider():
    global count, text
    if count>= len(txt) :
        count = -1
        label.configure(text=text)
    else:
        text = text + txt[count]
        label.configure(text=text)
        count += 1
        label.after(100, slider)
slider()

#Gestion chat

chatBox = ctk.CTkTextbox(app,
        width = 500,
        height=450,
        corner_radius=20,
        border_width=2,
        font=("Helvetica", 18),
        wrap="word",
        scrollbar_button_hover_color="gray")
chatBox.pack(side="top", fill="both", expand=True, padx=20, pady=(20, 10))
chatBox.configure(state="disabled")
chatBox.tag_config("user_style", lmargin1=20, lmargin2=20, foreground="#3B8ED0")
chatBox.tag_config("ai_style", lmargin1=5, lmargin2=5, foreground="white")


def update_chat(msg, tag="ai_style"):
    chatBox.configure(state="normal")
    chatBox.insert("end", msg, tag)
    chatBox.see("end")
    chatBox.configure(state="disabled")

# C'est la l'input user et sa gestion
textbox = ctk.CTkTextbox(app,
        width = 500,
        height=100,
        corner_radius=20,
        border_width=2,
        font=("Helvetica", 18),
        wrap="word",
        scrollbar_button_hover_color="gray")
textbox.insert("0.0", "Write something here...")
textbox.pack(side="left", fill="x", padx=(50, 0), expand=True)

def anti_lag(msg):
    initialization_chat(msg, callback=update_chat)

def send():
    msg = textbox.get(0.0, "end").strip()
    if msg != "":
        update_chat(f"\n\n\t\t\tYou : {msg}\n\n", "user_style")
        textbox.delete("0.0", "end")
        threading.Thread(target=anti_lag, args=(msg,)).start()

send_button = ctk.CTkButton(app,
        text="=>",
        width=50,
        height=40,
        corner_radius=10,
        command=send,
        fg_color="#3B8ED0")
send_button.pack(side="right", padx=(10, 0))


app.mainloop()

