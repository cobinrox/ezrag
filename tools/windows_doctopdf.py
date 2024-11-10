'''
Converts doc, docx to PDF.
For windows systems only, and must have MSWord installed.
'''
import os
import comtypes.client

def convert_to_pdf(input_path, output_path):
    """Convert a .doc or .docx file to a PDF."""
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False

    try:
        doc = word.Documents.Open(input_path)
        doc.SaveAs(output_path, FileFormat=17)  # FileFormat=17 corresponds to PDF
        doc.Close()
        print(f"Successfully converted {input_path} to {output_path}")
        return True
    except Exception as e:
        print(f"Failed to convert {input_path}: {e}")
        return False
    finally:
        word.Quit()

def walk_and_convert(folder_path):
    """Recursively walk through folder hierarchy and convert .doc/.docx files to PDF."""
    total_files_found = 0
    successful_conversions = 0
    failed_conversions = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.doc', '.docx')):
                total_files_found += 1
                input_file_path = os.path.join(root, file)
                base_name = os.path.splitext(file)[0]
                output_file_path = os.path.join(root, f"PDF_{base_name}.pdf")
                
                if convert_to_pdf(input_file_path, output_file_path):
                    successful_conversions += 1
                else:
                    failed_conversions += 1

    # Print summary after processing
    print("\n--- Conversion Summary ---")
    print(f"Total .doc/.docx files found: {total_files_found}")
    print(f"Successfully converted: {successful_conversions}")
    print(f"Failed to convert: {failed_conversions}")

if __name__ == "__main__":
    folder_name = input("Enter the folder path: ").strip()
    if os.path.isdir(folder_name):
        walk_and_convert(folder_name)
    else:
        print("Invalid folder path.")
