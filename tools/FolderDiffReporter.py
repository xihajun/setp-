import hashlib
import os
from multiprocessing import Pool, cpu_count

class FileComparer:
    def __init__(self, folder1, folder2):
        self.folder1 = folder1
        self.folder2 = folder2

    @staticmethod
    def md5_and_size(file_path):
        """Compute the MD5 hash and size of a file."""
        hash_md5 = hashlib.md5()
        size = 0
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                    size += len(chunk)
            return file_path, hash_md5.hexdigest(), size
        except Exception:
            return file_path, None, None

    def hash_files_in_folder(self, folder_path):
        """Compute MD5 hashes and sizes for all files in a folder, recursively, using multiprocessing."""
        pool = Pool(processes=cpu_count())
        files = [os.path.join(root, filename) for root, _, filenames in os.walk(folder_path) for filename in filenames]
        results = pool.map(self.md5_and_size, files)
        pool.close()
        pool.join()

        hashes = {os.path.relpath(path, start=folder_path): (hash_val, size) for path, hash_val, size in results if hash_val is not None}
        return hashes

    def compare_folders(self):
        """Compare the files in two folders by their MD5 hashes and sizes."""
        folder1_hashes = self.hash_files_in_folder(self.folder1)
        folder2_hashes = self.hash_files_in_folder(self.folder2)

        all_keys = set(folder1_hashes) | set(folder2_hashes)
        added, removed, modified, same = [], [], [], []

        for key in all_keys:
            in_folder1 = key in folder1_hashes
            in_folder2 = key in folder2_hashes

            if in_folder1 and not in_folder2:
                removed.append((key, folder1_hashes[key][1]))
            elif not in_folder1 and in_folder2:
                added.append((key, folder2_hashes[key][1]))
            elif folder1_hashes[key] != folder2_hashes[key]:
                modified.append((key, folder1_hashes[key][1], folder2_hashes[key][1]))
            else:
                same.append((key, folder1_hashes[key][1]))

        return added, removed, modified, same

    @staticmethod
    def color_text(text, color):
        """Return text wrapped in ANSI color codes."""
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "reset": "\033[0m"
        }
        return f"{colors[color]}{text}{colors['reset']}"

    def report_differences(self):
        """Prints out the differences and similarities between two folders with color coding."""
        added, removed, modified, same = self.compare_folders()

        print(f"Comparing:\n- FROM: {self.folder1}\n- TO:   {self.folder2}")

        if same:
            print("\nIdentical files (same MD5 and size):")
            for file, size in same:
                print(self.color_text(f"= {file} (size: {size} bytes)", "green"))

        if added:
            print("\nFiles to add (present in TO but not in FROM):")
            for file, size in added:
                print(self.color_text(f"+ {os.path.join(self.folder2, file)} (size: {size} bytes)", "red"))

        if removed:
            print("\nFiles to remove (present in FROM but not in TO):")
            for file, size in removed:
                print(self.color_text(f"- {os.path.join(self.folder1, file)} (size: {size} bytes)", "red"))

        if modified:
            print("\nFiles that have changed (different between FROM and TO):")
            for file, size1, size2 in modified:
                print(self.color_text(f"* {file} (FROM size: {size1} bytes, TO size: {size2} bytes)", "red"))

        if not (added or removed or modified or same):
            print(self.color_text("No differences or identical files found.", "green"))

if __name__ == "__main__":
    folder1 = input("Enter the path to the FROM folder: ")
    folder2 = input("Enter the path to the TO folder: ")
    comparer = FileComparer(folder1, folder2)
    comparer.report_differences()
