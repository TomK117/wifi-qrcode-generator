from __future__ import annotations

from pathlib import Path
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import qrcode


APP_TITLE = "Wi-Fi QR Code Generator"
OUTPUT_DIR = Path(__file__).resolve().parent / "qr-images"
SECURITY_OPTIONS = {
	"WPA/WPA2": "WPA",
	"WEP": "WEP",
	"Aucune (réseau ouvert)": "nopass",
}


def escape_wifi_value(value: str) -> str:
	escaped = value.replace("\\", "\\\\")
	for character in (";", ",", ":", '"'):
		escaped = escaped.replace(character, f"\\{character}")
	return escaped


def build_wifi_payload(ssid: str, password: str, security: str, hidden: bool) -> str:
	safe_ssid = escape_wifi_value(ssid)
	safe_password = escape_wifi_value(password)
	hidden_value = "true" if hidden else "false"

	if security == "nopass":
		return f"WIFI:T:{security};S:{safe_ssid};H:{hidden_value};;"

	return f"WIFI:T:{security};S:{safe_ssid};P:{safe_password};H:{hidden_value};;"


def sanitize_filename(value: str) -> str:
	cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
	return cleaned.strip("-._") or "wifi-network"


def generate_qr_image(payload: str, destination: Path) -> None:
	qr_code = qrcode.QRCode(version=1, box_size=10, border=4)
	qr_code.add_data(payload)
	qr_code.make(fit=True)

	image = qr_code.make_image(fill_color="black", back_color="white")
	destination.parent.mkdir(parents=True, exist_ok=True)
	image.save(destination)


class WifiQrApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title(APP_TITLE)
		self.root.resizable(False, False)
		self.root.columnconfigure(0, weight=1)

		self.ssid_var = tk.StringVar()
		self.password_var = tk.StringVar()
		self.security_var = tk.StringVar(value="WPA/WPA2")
		self.hidden_var = tk.BooleanVar(value=False)
		self.output_dir = OUTPUT_DIR
		self.status_var = tk.StringVar(value="Prêt à générer un QR code.")

		self._build_interface()

	def _build_interface(self) -> None:
		container = ttk.Frame(self.root, padding=18)
		container.grid(sticky="nsew")
		container.columnconfigure(1, weight=1)

		ttk.Label(container, text="Nom du réseau (SSID) :").grid(row=0, column=0, sticky="w", pady=(0, 8))
		ssid_entry = ttk.Entry(container, textvariable=self.ssid_var, width=34)
		ssid_entry.grid(row=0, column=1, sticky="ew", pady=(0, 8))

		ttk.Label(container, text="Mot de passe :").grid(row=1, column=0, sticky="w", pady=8)
		self.password_entry = ttk.Entry(container, textvariable=self.password_var, show="•", width=34)
		self.password_entry.grid(row=1, column=1, sticky="ew", pady=8)

		ttk.Label(container, text="Sécurité :").grid(row=2, column=0, sticky="w", pady=8)
		security_menu = ttk.Combobox(
			container,
			textvariable=self.security_var,
			values=list(SECURITY_OPTIONS.keys()),
			state="readonly",
			width=31,
		)
		security_menu.grid(row=2, column=1, sticky="ew", pady=8)
		security_menu.bind("<<ComboboxSelected>>", self._toggle_password_state)

		ttk.Checkbutton(container, text="Réseau masqué", variable=self.hidden_var).grid(
			row=3, column=1, sticky="w", pady=8
		)

		ttk.Button(container, text="Choisir le dossier de sortie", command=self.choose_output_directory).grid(
			row=4, column=0, columnspan=2, sticky="ew", pady=(8, 6)
		)
		ttk.Label(container, textvariable=self._output_label_var(), foreground="#555555").grid(
			row=5, column=0, columnspan=2, sticky="w", pady=(0, 12)
		)

		ttk.Button(container, text="Générer le QR code", command=self.generate).grid(
			row=6, column=0, columnspan=2, sticky="ew", pady=(0, 12)
		)

		ttk.Label(container, textvariable=self.status_var, wraplength=320, justify="left").grid(
			row=7, column=0, columnspan=2, sticky="w"
		)

		self._toggle_password_state()
		ssid_entry.focus_set()

	def _output_label_var(self) -> tk.StringVar:
		label_var = tk.StringVar(value=f"Dossier actuel : {self.output_dir}")

		def update_label(*_: object) -> None:
			label_var.set(f"Dossier actuel : {self.output_dir}")

		self._refresh_output_label = update_label
		return label_var

	def _toggle_password_state(self, *_: object) -> None:
		security = SECURITY_OPTIONS[self.security_var.get()]
		if security == "nopass":
			self.password_var.set("")
			self.password_entry.configure(state="disabled")
		else:
			self.password_entry.configure(state="normal")

	def choose_output_directory(self) -> None:
		selected = filedialog.askdirectory(initialdir=str(self.output_dir), title="Choisir le dossier de sortie")
		if selected:
			self.output_dir = Path(selected)
			self._refresh_output_label()
			self.status_var.set("Dossier de sortie mis à jour.")

	def generate(self) -> None:
		ssid = self.ssid_var.get().strip()
		password = self.password_var.get()
		security = SECURITY_OPTIONS[self.security_var.get()]
		hidden = self.hidden_var.get()

		if not ssid:
			messagebox.showerror("Champ requis", "Veuillez renseigner le nom du réseau Wi‑Fi.")
			return

		if security != "nopass" and not password:
			messagebox.showerror("Champ requis", "Veuillez renseigner le mot de passe du réseau.")
			return

		payload = build_wifi_payload(ssid=ssid, password=password, security=security, hidden=hidden)
		file_name = f"{sanitize_filename(ssid)}.png"
		destination = self.output_dir / file_name

		try:
			generate_qr_image(payload, destination)
		except OSError as error:
			messagebox.showerror("Erreur d'écriture", f"Impossible d'enregistrer l'image :\n{error}")
			return

		self.status_var.set(f"QR code généré : {destination}")
		messagebox.showinfo(
			"Succès",
			"Le QR code a été généré avec succès.\n"
			f"Fichier enregistré dans :\n{destination}",
		)


def main() -> None:
	root = tk.Tk()
	style = ttk.Style(root)
	if "clam" in style.theme_names():
		style.theme_use("clam")
	WifiQrApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
