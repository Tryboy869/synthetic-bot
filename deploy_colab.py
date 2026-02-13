#!/usr/bin/env python3
"""Synthetic Bot - GitHub Deployment Script v1.0.0-beta"""
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
REPO_NAME = "synthetic-bot"
import os, sys, json, requests, base64, tarfile, shutil
from pathlib import Path
IN_COLAB = False
try:
    from google.colab import files
    IN_COLAB = True
except: pass
if not IN_COLAB: print("⚠️ Run in Google Colab"); sys.exit(1)
try: import requests
except: os.system("pip install -q requests"); import requests

print("🚀 SYNTHETIC BOT DEPLOYMENT v1.0.0-beta\n")
if GITHUB_TOKEN == "ghp_YOUR_TOKEN_HERE": print("❌ Set GITHUB_TOKEN!"); sys.exit(1)
print(f"✅ Token: {'*'*10}{GITHUB_TOKEN[-10:]}\n📤 Upload .tar.gz file:\n")
uploaded = files.upload()
if not uploaded: sys.exit(1)
tar_file = list(uploaded.keys())[0]
print(f"✅ Uploaded: {tar_file}\n📦 Extracting...")
extract_dir = "/tmp/synthetic-bot"
if os.path.exists(extract_dir): shutil.rmtree(extract_dir)
with tarfile.open(tar_file, 'r:gz') as tar: tar.extractall("/tmp")
for item in os.listdir("/tmp"):
    if "synthetic-bot" in item and os.path.isdir(f"/tmp/{item}"):
        if f"/tmp/{item}" != extract_dir: shutil.move(f"/tmp/{item}", extract_dir)
        break
files_list = []
for root, dirs, files in os.walk(extract_dir):
    for file in files: files_list.append(os.path.relpath(os.path.join(root, file), extract_dir))
print(f"✅ Extracted {len(files_list)} files\n🔐 Authenticating...")
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
user_response = requests.get("https://api.github.com/user", headers=headers)
if user_response.status_code != 200: print("❌ Auth failed"); sys.exit(1)
username = user_response.json()['login']
print(f"✅ Authenticated: {username}\n📦 Creating repo...")
repo_response = requests.post("https://api.github.com/user/repos", headers=headers, json={"name": REPO_NAME, "description": "Multi-language self-correcting bots", "private": False})
if repo_response.status_code == 201: print(f"✅ Created: https://github.com/{username}/{REPO_NAME}")
elif "already exists" in repo_response.text: print(f"⚠️ Repo exists, updating...")
else: print(f"❌ Failed: {repo_response.json()}"); sys.exit(1)
print(f"\n⬆️ Uploading {len(files_list)} files...\n")
uploaded_count = 0
for file_path in files_list:
    if any(p in file_path for p in ['.pyc', '__pycache__']): continue
    full_path = os.path.join(extract_dir, file_path)
    with open(full_path, 'rb') as f: content = f.read()
    content_b64 = base64.b64encode(content).decode()
    upload_data = {"message": f"Add {file_path}", "content": content_b64}
    url = f"https://api.github.com/repos/{username}/{REPO_NAME}/contents/{file_path}"
    check = requests.get(url, headers=headers)
    if check.status_code == 200: upload_data["sha"] = check.json()["sha"]; upload_data["message"] = f"Update {file_path}"
    response = requests.put(url, headers=headers, json=upload_data)
    if response.status_code in [200, 201]: uploaded_count += 1; print(f"   ✓ {file_path}")
    else: print(f"   ✗ {file_path}")
print(f"\n{'='*70}\n🎉 DEPLOYMENT COMPLETE\n{'='*70}\n\n📍 https://github.com/{username}/{REPO_NAME}\n\n✨ Next: Visit repo, enable Actions, star it!\n{'='*70}")
