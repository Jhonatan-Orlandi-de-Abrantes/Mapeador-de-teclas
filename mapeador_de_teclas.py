import tkinter as tk, threading, pickle, os, time, keyboard
from tkinter import messagebox

MAPPING_FILE = "mapping.pkl"
HOTKEYS_FILE = "hotkeys.pkl"

class MapperApp:
    def __init__(self, root):
        self.root = root
        root.title("Mapeador de Teclas")
        root.geometry("520x220")
        root.resizable(False, False)

        self.hotkey_record = "F9"
        self.hotkey_start = "F10"
        self.trigger_key = "F8"

        self.load_hotkeys()

        self._recording = False
        self.looping = False
        self.loop_thread = None
        self._trigger_playing = False

        self._build_ui()
        self.register_hotkeys()
        self.update_mapping_label()

    # ---------- UI ----------
    def _build_ui(self):
        fr = tk.Frame(self.root, padx=12, pady=12)
        fr.pack(fill="both", expand=True)

        lbl_aviso = tk.Label(fr, text="ATENÇÃO!!! Em caso de perigo, use Ctrl+Alt+Del.", fg="red", font=("Arial", 10))
        lbl_aviso.pack(pady=(0, 10))

        frame_atalhos = tk.Frame(fr)
        frame_atalhos.pack()

        tk.Label(frame_atalhos, text="Atalho Gravar:").grid(row=0, column=0, sticky="w")
        self.lbl_hotkey_record = tk.Label(frame_atalhos, text=self.hotkey_record, width=10, relief="sunken")
        self.lbl_hotkey_record.grid(row=0, column=1, sticky="w", padx=(6,0))
        tk.Button(frame_atalhos, text="Definir", command=lambda: threading.Thread(target=self.set_hotkey, args=("record",)).start()).grid(row=0, column=2, padx=6)

        tk.Label(frame_atalhos, text="Atalho Iniciar Loop:").grid(row=1, column=0, sticky="w")
        self.lbl_hotkey_start = tk.Label(frame_atalhos, text=self.hotkey_start, width=10, relief="sunken")
        self.lbl_hotkey_start.grid(row=1, column=1, sticky="w", padx=(6,0))
        tk.Button(frame_atalhos, text="Definir", command=lambda: threading.Thread(target=self.set_hotkey, args=("start",)).start()).grid(row=1, column=2, padx=6)

        tk.Label(frame_atalhos, text="Atalho Reproduzir uma vez").grid(row=2, column=0, sticky="w")
        self.lbl_trigger = tk.Label(frame_atalhos, text=self.trigger_key, width=10, relief="sunken")
        self.lbl_trigger.grid(row=2, column=1, sticky="w", padx=(6,0))
        tk.Button(frame_atalhos, text="Definir tecla", command=lambda: threading.Thread(target=self.define_trigger_key).start()).grid(row=2, column=2, padx=6)

        tk.Label(frame_atalhos, text="Mapeamento salvo:").grid(row=3, column=0, sticky="w", pady=(12,0))
        self.lbl_mapping = tk.Label(frame_atalhos, text="(Nenhum)", width=30, anchor="w", relief="sunken")
        self.lbl_mapping.grid(row=3, column=1, columnspan=2, sticky="w", pady=(12,0))

        btn_frame = tk.Frame(fr)
        btn_frame.pack(pady=(14,0))
        tk.Button(btn_frame, text="Gravar mapeamento", command=lambda: threading.Thread(target=self.on_record_button).start(), width=20).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Iniciar/Parar loop", command=lambda: threading.Thread(target=self.on_start_loop_button).start(), width=20).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="Reproduzir uma vez", command=lambda: threading.Thread(target=self.trigger_mapping_once).start(), width=20).grid(row=0, column=2, padx=8)

    def update_mapping_label(self):
        if os.path.exists(MAPPING_FILE):
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(MAPPING_FILE)))
            self.lbl_mapping.config(text=f"Existente (salvo: {mtime})")
        else: self.lbl_mapping.config(text="(Nenhum)")

    # ---------- Hotkeys persistência ----------
    def save_hotkeys(self):
        try:
            with open(HOTKEYS_FILE, "wb") as f:
                pickle.dump({
                    "record": self.hotkey_record,
                    "start": self.hotkey_start,
                    "trigger": self.trigger_key
                }, f)
        except Exception as e: print("Erro ao salvar hotkeys:", e)

    def load_hotkeys(self):
        if os.path.exists(HOTKEYS_FILE):
            try:
                with open(HOTKEYS_FILE, "rb") as f:
                    data = pickle.load(f)
                    self.hotkey_record = data.get("record", self.hotkey_record)
                    self.hotkey_start = data.get("start", self.hotkey_start)
                    self.trigger_key = data.get("trigger", self.trigger_key)
            except Exception as e:
                print("Erro ao carregar hotkeys:", e)

    def register_hotkeys(self):
        try: keyboard.remove_hotkey(self.hotkey_record)
        except: pass
        try: keyboard.remove_hotkey(self.hotkey_start)
        except: pass
        try: keyboard.remove_hotkey(self.trigger_key)
        except: pass
        try:
            keyboard.add_hotkey(self.hotkey_record, lambda: threading.Thread(target=self.on_record_button).start())
            keyboard.add_hotkey(self.hotkey_start, lambda: threading.Thread(target=self.on_start_loop_button).start())
            keyboard.add_hotkey(self.trigger_key, lambda: threading.Thread(target=self.trigger_mapping_once).start())
        except Exception as e:
            print("Erro ao registrar hotkeys:", e)

    # ---------- Definir hotkeys via modal ----------
    def set_hotkey(self, which):
        title = "Definir atalho para Gravar" if which == "record" else "Definir atalho para Iniciar Loop"
        key = self.capture_single_key_modal(title)
        key = key
        if not key: return
        try:
            if which == "record":
                try: keyboard.remove_hotkey(self.hotkey_record)
                except: pass
                self.hotkey_record = key.upper()
                self.lbl_hotkey_record.config(text=self.hotkey_record)

            else:
                try: keyboard.remove_hotkey(self.hotkey_start)
                except: pass
                self.hotkey_start = key
                self.lbl_hotkey_start.config(text=self.hotkey_start)
            self.save_hotkeys()
            self.register_hotkeys()
            messagebox.showinfo("Ok", f"Tecla definida: {key.upper()}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao definir hotkey: {e}")

    def define_trigger_key(self):
        key = self.capture_single_key_modal("Defina a tecla de reprodução única")
        if not key: return
        try:
            try: keyboard.remove_hotkey(self.trigger_key)
            except: pass
            self.trigger_key = key.upper()
            self.lbl_trigger.config(text=self.trigger_key)
            self.save_hotkeys()
            self.register_hotkeys()
            messagebox.showinfo("Ok", f"Tecla de reprodução única definida: {key.upper()}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao definir tecla de reprodução única: {e}")

    def capture_single_key_modal(self, title):
        result = {"key": None}
        modal = tk.Toplevel(self.root)
        modal.title(title)
        modal.geometry("380x120")
        modal.transient(self.root)
        modal.grab_set()
        tk.Label(modal, text=title, font=("Arial", 11)).pack(pady=(10, 6))
        lbl = tk.Label(modal, text="Aguarde... pressione uma tecla no teclado", fg="blue")
        lbl.pack(pady=(6,6))

        def worker():
            try:
                k = keyboard.read_key()
                if k:
                    result["key"] = k.upper()
                    self.root.after(0, lambda: finalize(k))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao ler tecla: {e}"))

        def finalize(key):
            lbl.config(text=f"Tecla detectada: {key.upper()}")
            tk.Button(modal, text="Confirmar", command=lambda: modal.destroy()).pack(pady=(8,10))

        threading.Thread(target=worker, daemon=True).start()
        self.root.wait_window(modal)
        return result["key"]

    # ---------- Gravação ----------
    def on_record_button(self):
        if self._recording:
            return
        if os.path.exists(MAPPING_FILE):
            if not messagebox.askyesno("Sobrescrever?", "Já existe um mapeamento salvo. Deseja sobrescrevê-lo?"):
                return

        self._recording = True
        stop_key = self.hotkey_record

        info = tk.Toplevel(self.root)
        info.title("Gravando...")
        info.geometry("410x90")
        tk.Label(info, text=f"Gravando... pressione '{stop_key}' novamente para parar.").pack(pady=12)
        info.grab_set()

        def worker():
            recorded = []
            start_time = None
            try:
                while self._recording:
                    e = keyboard.read_event(suppress=False)
                    if start_time is None:
                        start_time = e.time
                    recorded.append(e)
                    if e.event_type == "down" and e.name.upper() == stop_key.upper():
                        self._recording = False
                        break
                with open(MAPPING_FILE, "wb") as f:
                    pickle.dump(recorded, f)
                self.root.after(0, lambda: messagebox.showinfo("Pronto", f"Gravação salva com {len(recorded)} eventos."))
                self.root.after(0, self.update_mapping_label)
            except Exception as ex:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante gravação: {ex}"))
            finally:
                self._recording = False
                self.root.after(0, info.destroy)

        threading.Thread(target=worker, daemon=True).start()

    # ---------- Carregar mapeamento ----------
    def load_mapping(self):
        if not os.path.exists(MAPPING_FILE):
            return None
        try:
            with open(MAPPING_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar mapeamento: {e}")
            return None

    # ---------- Reprodução manual baseada em eventos ----------
    def _play_recorded_once(self, recorded, speed=1.0):
        if not recorded:
            return
        prev_time = recorded[0].time
        try:
            for ev in recorded:
                if (not self._trigger_playing) and (not self.looping):
                    break
                delay = (ev.time - prev_time) / speed
                if delay > 0:
                    waited = 0.0
                    step = 0.01
                    while waited < delay:
                        if (not self._trigger_playing) and (not self.looping):
                            return
                        time.sleep(min(step, delay - waited))
                        waited += step
                try:
                    if ev.event_type == "down":
                        keyboard.press(ev.name)
                    elif ev.event_type == "up":
                        keyboard.release(ev.name)
                except Exception: pass
                prev_time = ev.time
        finally: return

    # ---------- Tecla de reprodução única ----------
    def trigger_mapping_once(self):
        if self._trigger_playing:
            self._trigger_playing = False
            return

        recorded = self.load_mapping()
        if not recorded:
            messagebox.showwarning("Nenhum mapeamento", "Não há mapeamento salvo.")
            return

        self._trigger_playing = True

        def worker():
            try:
                self._play_recorded_once(recorded, speed=1.0)
            finally:
                self._trigger_playing = False

        threading.Thread(target=worker, daemon=True).start()

    # ---------- Loop contínuo ----------
    def on_start_loop_button(self):
        if self.looping:
            self.looping = False
            if self.loop_thread:
                self.loop_thread.join(timeout=0.5)
            return

        recorded = self.load_mapping()
        if not recorded:
            messagebox.showwarning("Nenhum mapeamento", "Não há mapeamento salvo.")
            return

        if not messagebox.askyesno("Iniciar loop?", f"Deseja iniciar o loop contínuo?\n(Pressione '{self.hotkey_start}' novamente para parar)"):
            return

        self.looping = True

        def loop_worker():
            try:
                while self.looping:
                    self._play_recorded_once(recorded, speed=1.0)
                    for _ in range(10):
                        if not self.looping:
                            break
                        time.sleep(0.01)
            finally:
                self.looping = False

        self.loop_thread = threading.Thread(target=loop_worker, daemon=True)
        self.loop_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MapperApp(root)
    root.mainloop()
