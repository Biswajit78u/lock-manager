# Lock Manager

Lock Manager is a Windows desktop application that lets you restrict access to folders and executable files using real NTFS permission changes — not just hiding files. Built with Python for the interface and a lightweight C DLL for the underlying lock/unlock operations.

## Features
- Lock/unlock folders and `.exe` files via Windows permissions (`icacls`)
- Password protection using Windows DPAPI encryption (tied to your Windows account)
- Persistent locked-items list stored in `%APPDATA%`
- Clean, modern UI built with CustomTkinter
- Packaged as a proper Windows installer (via Inno Setup) with Start Menu shortcuts and uninstall support

## Tech stack
- Python (CustomTkinter for UI)
- C (compiled to a DLL, called via `ctypes`)
- PyInstaller for packaging
- Inno Setup for the Windows installer

## Disclaimer
This project uses OS-level permission changes for basic access restriction. It is intended as a personal/learning project and does not provide military-grade security guarantees.
