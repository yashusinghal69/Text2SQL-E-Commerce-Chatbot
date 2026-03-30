import kagglehub
import shutil
import os

path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
data_folder = "E-Commerce_Dataset"

os.makedirs(data_folder, exist_ok=True)
 
print(f"\nDownloading files to '{data_folder}' folder")
for item in os.listdir(path):
    source = os.path.join(path, item)
    destination = os.path.join(data_folder, item)
    
    if os.path.isfile(source):
        shutil.copy2(source, destination)
        print(f"Copied: {item}")

print(f"\nAll files saved to '{data_folder}' folder")