# core/zipper.py

import os
import shutil
import zipfile
import argparse

class Zipper:
    def __init__(self, temp_dir="tmp_zip"):
        self.temp_dir = temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)

    def zip_proxy(self, proxy_path):
        """
        Zips the given proxy directory and stores it in the temp directory.
        :param proxy_path: Path to the proxy directory.
        :return: Path to the zipped file.
        """
        if not os.path.isdir(proxy_path):
            raise ValueError(f"Proxy path {proxy_path} is not a directory")

        proxy_name = os.path.basename(os.path.normpath(proxy_path))
        zip_filename = f"{proxy_name}.zip"
        zip_path = os.path.join(self.temp_dir, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(proxy_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, start=proxy_path)
                    zipf.write(full_path, arcname)

        return zip_path

    def cleanup(self, zip_path):
        """
        Deletes the specified zip file.
        :param zip_path: Path to the zipped file to be deleted.
        """
        if os.path.exists(zip_path):
            os.remove(zip_path)

    def cleanup_all(self):
        """
        Deletes the entire temp directory used for zipping.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


def main():
    parser = argparse.ArgumentParser(description="Zip an Apigee proxy directory.")
    parser.add_argument("proxy_path", help="Path to the Apigee proxy directory to zip.")
    parser.add_argument("--cleanup", action="store_true", help="Clean up the zip file after creation.")
    args = parser.parse_args()

    zipper = Zipper()
    try:
        zip_path = zipper.zip_proxy(args.proxy_path)
        if args.cleanup:
            zipper.cleanup(zip_path)
            print(f"Deleted zip file: {zip_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()