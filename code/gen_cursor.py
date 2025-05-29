# -*- coding: utf-8 -*-
"""
DESCRIPTION:
This script automates interactions with a software tool called "Cursor" to generate code suggestions 
using a specified AI model (e.g., GPT-4). It utilizes the `pyautogui` library for GUI automation and 
`pyperclip` for clipboard operations. The script processes Python files in a specified folder, 
generates code suggestions for specified lines, and saves the results to a designated output folder.
FUNCTIONS:
- close_window(): Closes the current Cursor window, handling any confirmation dialogs.
- wait_for_image(image_path, timeout, confidence): Waits for an image to appear on the screen within a specified timeout.
- wait_for_confirm(image_path, timeout, confidence): Waits for an image to appear and confirms it within a specified timeout.
- copy_all(): Copies all content from the current editor in Cursor and returns it as a string.
- automate_cursor_interaction(file_path, filename, fold, model): Automates the process of generating code suggestions 
    for a given Python file using Cursor and saves the results.
USAGE:
1. Specify the folder containing Python files to process (`folder_path`).
2. Set the desired AI model (e.g., 'gpt4').
3. Run the script to process files in reverse order, generating code suggestions and saving them to the output folder.
NOTES:
- Ensure the paths to Cursor executable and required images (e.g., 'accept.png', 'gencur.png') are correctly configured.
- The script includes sleep intervals to comply with Cursor's rate limits and avoid potential bans.
- The script handles errors such as missing images or Unicode encoding issues gracefully.
- This code can only run on Windows. Please adjust the click position parameters according to your screen resolution before running, and modify the images used based on the appearance of your compiler.
DEPENDENCIES:
- pyautogui
- pyperclip
- time
- os
- subprocess
"""

import pyautogui, pyperclip
import time
import os
import subprocess

def close_window():
    # Close the current cursor window
    ok = wait_for_image('accept.png', timeout=3, confidence=0.9)
    if not ok:
        pass
    else:
        pyautogui.click(ok)
    # Please adjust this parameter according to your device's screen resolution.
    pyautogui.click(x=1456, y=165)
    pyautogui.click(x=1456, y=683)
    pyautogui.hotkey('ctrl', 'w')
    ok = wait_for_image('dontsave.png', timeout=1)
    if not ok:
        return
    else:
        pyautogui.click(ok)

def wait_for_image(image_path, timeout=8, confidence=0.6):
    """Wait for an image to appear on the screen within a specified timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except pyautogui.ImageNotFoundException as e:
            location = False
        if location:
            return location
        time.sleep(2)  
    return False

def wait_for_confirm(image_path, timeout=8, confidence=0.6):
    """Wait for an image to appear on the screen and confirm it within a specified timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except pyautogui.ImageNotFoundException as e:
            location = False
        if location:
            return location
        time.sleep(2)

        if int(time.time() - start) % 5 == 0:
            location = wait_for_image('gencur.png', timeout=3, confidence=0.7)
            if location:
                pyautogui.click(location)
            else:
                pass
            
    return False

def copy_all():
    """Copy all content from the current editor in cursor."""
    ok = wait_for_image('tempy2.png', timeout=1)
    if not ok:
        ok = wait_for_image('tempy.png', timeout=1)
        if not ok:
            return False
    pyautogui.click(ok)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'c')
    now_content = pyperclip.paste()

    return now_content

def automate_cursor_interaction(file_path, filename, fold, model='gpt4'):
    """Automate interaction with cursor to generate code suggestions using CUrsor."""
    with open(file_path, 'r', encoding='utf-8') as file:
        script = file.read()
    
    parts = filename.split('_')
    num_lines = int(parts[1]) + 1
    start_line = int(parts[2])

    copilot_call_attempt = 0
    
    copilot_suggestion_path = os.path.join(
        fold,
        filename.replace(".py", f"_{model}_{copilot_call_attempt}.py"),
    )

    if os.path.exists(copilot_suggestion_path):
        return
    
    with open('tem.py', 'w', encoding='utf-8') as temp_file:
        temp_file.write(script)
    time.sleep(3)
    subprocess.call(
        [
            r"your  Cursor.exe  path",
            os.path.join('tem.py'),
        ]
        , shell=True
    )

    ok = wait_for_image('tempy.png', confidence=0.4)
    if not ok:
        close_window()
        return

    pyautogui.click(x=1317, y=165)
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'g')  # open Go to Line dialog
    wait_for_image('linetogo.png', confidence=0.5)
    if start_line == 0:
        start_line = 1
    pyautogui.write(str(start_line), interval=0.2)  # write the line number to go to
    time.sleep(2)
    pyautogui.press('enter')  # press Enter to go to the specified line
    
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'k')
    time.sleep(2)
    wait_for_image('ask_cur.png')
    
    if num_lines == 1:
        prompt = f"Please complete a line of code here."  # prompt text
    else:
        prompt = f"Please complete {num_lines} lines of code here."
    pyautogui.write(prompt, interval=0.2)

    ok = wait_for_image('gencur.png', timeout=10, confidence=0.7)
    if not ok:
        close_window()
        return
    time.sleep(3)
    pyautogui.click(ok)
    
    time.sleep(2)
    
    ok = wait_for_confirm('accept.png', timeout=3600, confidence=0.7)
    if not ok:
        close_window()
        return
    time.sleep(3)
    pyautogui.click(ok)
    time.sleep(1)
    clipboard_content = copy_all()
    try:
        with open(copilot_suggestion_path, "w", encoding="utf-8") as f:
            clipboard_content = pyperclip.paste()
            lines = clipboard_content.splitlines()
            modified_content = "\n".join(line.rstrip('\r\n') for line in lines)
            f.write(modified_content)
            f.close()
    except UnicodeEncodeError as e:
        close_window()
        return
    
    # Please do not easily reduce the sleep time here. 
    # Cursor officially imposes a limit on the frequency of calls. 
    # Reducing the interval may result in an irreversible ban. 
    # Even with a 90-second sleep time, you should not generate continuously for an extended period.
    time.sleep(90)  # wait for 90 seconds before processing the next file

    # Close the Cursor window after processing
    close_window()

if __name__ == '__main__':
    model = 'gpt4'
    
    folder_path = rf'your path' # Replace with your directory path
    
    fold = rf'{folder_path}\{model}'
    if not os.path.exists(fold):
        os.makedirs(fold)
    # Iterate through all Python files in the specified folder
    nums = 0
    for filename in reversed(os.listdir(folder_path)):
        if filename.endswith('.py'):
            file_path = os.path.join(folder_path, filename)
            automate_cursor_interaction(file_path, filename, fold, model=model)
            nums += 1
            print(f"Processed {nums} files in {fold}")

