import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

def add_period_to_srt(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        new_lines = []
        is_content_line = False  # A flag to determine if a line is content
        for line in lines:
            if '-->' in line:
                new_lines.append(line)
                is_content_line = True  # Following lines are content until a blank line
            elif line.strip().isdigit():
                new_lines.append(line)
                is_content_line = False  # Reset flag after sequence number
            elif line == '\n':  # Reset on blank lines as well
                new_lines.append(line)
                is_content_line = False
            else:
                if is_content_line:
                    line_content = line.strip()
                    if line_content and not line_content.endswith("。"):
                        line_content += "。"
                    new_lines.append(line_content + "\n")
                else:
                    new_lines.append(line)
        save_path = filepath.replace('.srt', '_period_added.srt')
        with open(save_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        messagebox.showinfo("Success", "Periods added successfully. New file saved as " + save_path)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def separate_srt(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Split the content into subtitle blocks
        subtitle_blocks = re.split(r'\n\s*\n', content.strip())

        timestamps = []
        subtitle_content = []

        for block in subtitle_blocks:
            lines = block.split('\n')
            if len(lines) >= 2:
                # The first line is the sequence number
                timestamps.append(lines[0] + '\n')
                # The second line is the timestamp
                timestamps.append(lines[1] + '\n\n')
                # The rest is the subtitle content
                content_text = ' '.join(lines[2:]).replace('\n', ' ').strip()
                subtitle_content.append(content_text)

        # Join all subtitle content into a single paragraph
        full_content = ' '.join(subtitle_content)

        # Write to separate files
        timestamp_path = filepath.replace('.srt', '_timestamps.srt')
        content_path = filepath.replace('.srt', '_content.txt')

        with open(timestamp_path, 'w', encoding='utf-8') as t_file:
            t_file.writelines(timestamps)

        with open(content_path, 'w', encoding='utf-8') as c_file:
            c_file.write(full_content)

        messagebox.showinfo("Success", "File has been successfully separated into timestamps and content.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def reattach_srt(timestamps_path, content_path, output_path):
    try:
        with open(timestamps_path, 'r', encoding='utf-8') as t_file:
            timestamps = t_file.read().split('\n\n')
        with open(content_path, 'r', encoding='utf-8') as c_file:
            content = c_file.read().strip()

        # Split content into sentences
        sentences = re.split(r'(?<=[。！？.])\s*', content)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            for i, (ts, sentence) in enumerate(zip(timestamps, sentences), 1):
                if ts.strip():
                    # Extract sequence number and timestamp
                    ts_lines = ts.strip().split('\n')
                    if len(ts_lines) >= 2:
                        seq_num = ts_lines[0]
                        timestamp = ts_lines[1]

                        # Write sequence number, timestamp, and corresponding sentence
                        output_file.write(f"{seq_num}\n")
                        output_file.write(f"{timestamp}\n")
                        output_file.write(sentence.strip() + '\n\n')

        messagebox.showinfo("Success", "Reattachment successful. New file saved as " + output_path)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def open_file_dialog(operation):
    if operation == "add_period" or operation == "separate":
        filepath = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
        if filepath:
            if operation == "add_period":
                add_period_to_srt(filepath)
            elif operation == "separate":
                separate_srt(filepath)
    elif operation == "reattach":
        timestamps_path = filedialog.askopenfilename(title="Select Timestamps File", filetypes=[("SRT files", "*.srt")])
        if timestamps_path:
            content_path = filedialog.askopenfilename(title="Select Content File", filetypes=[("Text files", "*.txt")])
            if content_path:
                output_path = filedialog.asksaveasfilename(title="Save Reattached File", filetypes=[("SRT files", "*.srt")], defaultextension=".srt")
                if output_path:
                    reattach_srt(timestamps_path, content_path, output_path)

def create_tab(parent, title, operation):
    frame = ttk.Frame(parent)
    btn_open = tk.Button(frame, text=f"Open File(s) to {title}", command=lambda: open_file_dialog(operation))
    btn_open.pack(expand=True, pady=20)
    return frame

def main():
    root = tk.Tk()
    root.title("SRT File Processor")
    root.geometry("500x300")
    tab_control = ttk.Notebook(root)
    add_period_tab = create_tab(tab_control, "Add Period", "add_period")
    separate_tab = create_tab(tab_control, "Separate", "separate")
    reattach_tab = create_tab(tab_control, "Reattach", "reattach")
    tab_control.add(add_period_tab, text='Add Period')
    tab_control.add(separate_tab, text='Separate')
    tab_control.add(reattach_tab, text='Reattach')
    tab_control.pack(expand=1, fill="both")
    root.mainloop()

if __name__ == "__main__":
    main()