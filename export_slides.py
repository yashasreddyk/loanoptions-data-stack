import os
import sys
import subprocess
import zipfile

out_dir = os.path.abspath("slide_images")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

try:
    print("Attempting to use comtypes (PowerPoint COM automation)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "comtypes", "--quiet"])
    import comtypes.client
    
    pptx_path = os.path.abspath("Join Our Team 2026 - Employee Info Pack.pptx")
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    # Open the presentation headless
    presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
    # Save as PNG (18)
    presentation.SaveAs(out_dir, 18)
    presentation.Close()
    powerpoint.Quit()
    print("Success using comtypes.")
    sys.exit(0)

except Exception as e:
    print(f"comtypes failed: {e}")

# If comtypes fails, just extract the zip to get the raw media images as a fallback
print("Attempting to extract zip media as a fallback...")
media_dir = os.path.join(out_dir, "media_fallback")
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

with zipfile.ZipFile("Join Our Team 2026 - Employee Info Pack.pptx", 'r') as zip_ref:
    for info in zip_ref.infolist():
        if info.filename.startswith("ppt/media/"):
            zip_ref.extract(info, media_dir)

print(f"Extracted raw media to {media_dir}")
