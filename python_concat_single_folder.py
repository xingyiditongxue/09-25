import os

def concat_files(input_folder, output_file):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in os.listdir(input_folder):
            filepath = os.path.join(input_folder, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as infile:
                        outfile.write(f"\n===== {filename} =====\n\n")  # optional: separator
                        outfile.write(infile.read())
                        outfile.write("\n\n")
                except Exception as e:
                    print(f"Skipping {filename}: {e}")

if __name__ == "__main__":
    folder = "/home/oxyl/Téléchargements/langgenius-gemini_0.5.4"      # 👈 put your folder path
    output = "all_concatenated.txt"  # 👈 name of the output file
    concat_files(folder, output)
    print(f"Concatenated content saved to {output}")
