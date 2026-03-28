# wifi-qrcode-generator

Application Python avec interface graphique simple pour générer un QR code Wi‑Fi.

## Fonctionnalités

- saisie du nom du réseau (`SSID`)
- saisie du mot de passe
- choix du type de sécurité (`WPA/WPA2`, `WEP`, réseau ouvert)
- option pour réseau masqué
- export automatique du QR code au format `PNG`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Lancement

```bash
source .venv/bin/activate
python main.py
```

Les fichiers générés sont enregistrés par défaut dans le dossier `qr-images/`.

## Format du QR code

Le QR code suit le format standard Wi‑Fi lisible par les smartphones :

```text
WIFI:T:WPA;S:NomDuReseau;P:MotDePasse;H:false;;
```