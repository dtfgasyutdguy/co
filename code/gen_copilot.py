# -*- coding: utf-8 -*-
import pyautogui, pyperclip
import time
import os
import subprocess

"""
DESCRIPTION:
This script automates interactions with Visual Studio Code (VSCode) to generate code suggestions using GitHub Copilot. 
It performs tasks such as opening files, navigating to specific lines, triggering Copilot suggestions, and saving the 
generated code to new files. The script is designed to handle multiple Python files in a specified folder and process 
them sequentially.
FUNCTIONALITY:
1. Automates VSCode interactions:
    - Opens a temporary file in VSCode.
    - Navigates to specific lines in the file.
    - Triggers GitHub Copilot suggestions.
    - Copies the generated code to the clipboard and saves it to a new file.
2. Handles errors and retries:
    - Detects and handles cases where Copilot suggestions fail.
    - Implements retries for clipboard operations and image-based interactions.
3. Image-based automation:
    - Uses `pyautogui` to locate and interact with UI elements based on screenshots.
    - Waits for specific images to appear or disappear on the screen.
4. Clipboard management:
    - Copies content from the clipboard and verifies its integrity.
    - Saves the generated code to a new file with a structured naming convention.
5. Rate limiting:
    - Introduces delays between Copilot calls to avoid exceeding usage limits.
USAGE:
- The script is executed as a standalone program.
- Specify the folder containing Python files to process.
- The script will create a subfolder for the generated files based on the specified model (e.g., GPT-4).
DEPENDENCIES:
- pyautogui: For automating UI interactions.
- pyperclip: For clipboard operations.
- subprocess: For launching VSCode.
- os, time: For file and time management.
NOTES:
- Ensure that the required images (e.g., 'tempy.png', 'ask.png', 'bar.png') are available in the working directory.
- The script is tailored for a specific workflow and may require adjustments for different setups.
- Avoid reducing the sleep time between Copilot calls to prevent rate-limiting issues.
- This code can only run on Windows. Please adjust the click position parameters according to your screen resolution before running, and modify the images used based on the appearance of your compiler.
DISCLAIMER:
- This script interacts with VSCode and GitHub Copilot in an automated manner. Use responsibly and ensure compliance 
  with the terms of service of the tools being used.
"""

def close_window():
    # close the current VSCode window
    ok = wait_for_image('tempy.png', timeout=2)
    if not ok:
        return
    # Please adjust this parameter according to your device's screen resolution.
    pyautogui.click(x=1456, y=165)
    pyautogui.click(x=1456, y=683)
    ok = click_if_exists('cancel.png')
    if ok:
        pyautogui.click(ok)
    ok = click_if_exists('discard.png')
    if ok:
        pyautogui.click(ok)
    pyautogui.hotkey('ctrl', 'w')
    ok = wait_for_image('dontsave.png', timeout=1)
    if not ok:
        return
    else:
        pyautogui.click(ok)

def click_if_exists(image_path, confidence=0.6):
    """Check if an image exists on the screen and click it if found."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    except pyautogui.ImageNotFoundException as e:
        return False
    if location:
        return True
    return False

def wait_time(times=10):
    """Wait for a specified number of seconds."""
    time.sleep(times)

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

def wait_for_image_go(image_path, timeout=8, confidence=0.6):
    """Wait for an image to disappear from the screen within a specified timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except pyautogui.ImageNotFoundException as e:
            location = False
        if not location:
            return True
        time.sleep(2)
    return False

def copy_to_clipboard(raw = '', timeout=8):
    """Copy the content of the clipboard, retrying if necessary."""
    start = time.time()
    content = ''
    now_content = '0'
    while time.time() - start < timeout and (content != now_content or now_content == raw):
        content = now_content
        ok = wait_for_image('tempy.png', timeout=1)
        if not ok:
            return False
        pyautogui.click(ok)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'c')
        
        ok = check_if_failed()
        if ok:
            return False
        now_content = pyperclip.paste()
    if time.time() - start >= timeout:
        return False
    return now_content
    
def copy_retry_to_clipboard(raw = '', timeout=8):
    """Copy the content of the clipboard, retrying if necessary."""
    start = time.time()
    content = ''
    now_content = '0'
    while time.time() - start < timeout and content != now_content:
        if now_content == raw:
            return False
        content = now_content
        ok = wait_for_image('tempy.png', timeout=1)
        if not ok:
            return False
        pyautogui.click(ok)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'c')
        
        ok = check_if_failed()
        if ok:
            return 'wtf'
        now_content = pyperclip.paste()
    if time.time() - start >= timeout:
        return False
    return now_content

def copy_all():
    # Copy all content from the current VSCode window to the clipboard.
    ok = wait_for_image('tempy.png', timeout=1)
    if not ok:
        return False
    pyautogui.click(ok)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'c')
    now_content = pyperclip.paste()

    return now_content

def check_if_failed():
    """Check if the Copilot suggestion failed by looking for specific images."""
    first = False
    second = False
    try:
        location = pyautogui.locateOnScreen('noresult.png', confidence=0.9)
    except pyautogui.ImageNotFoundException as e:
        first = True
    
    try:
        location = pyautogui.locateOnScreen('fail.png', confidence=0.9)
    except pyautogui.ImageNotFoundException as e:
        second = True
    
    if first and second:
        return False
    return True

# Automate interaction with VSCode to generate code suggestions using GitHub Copilot.
def automate_vscode_interaction(file_path, filename, fold, model='gpt4'):
    with open(file_path, 'r', encoding='utf-8') as file:
        script = file.read()
    
    parts = filename.split('_')
    num_lines = int(parts[1]) + 1
    start_line = int(parts[2])

    copilot_call_attempt = 0
    
    # create a new file and write the script to it
    copilot_suggestion_path = os.path.join(
        fold,
        filename.replace(".py", f"_{model}_{copilot_call_attempt}.py"),
    )

    if os.path.exists(copilot_suggestion_path):
        return
    # Create the directory if it doesn't exist
    with open('tem.py', 'w', encoding='utf-8') as temp_file:
        temp_file.write(script)
    subprocess.call(
        [
            "code",
            os.path.join('tem.py'),
        ]
        , shell=True
    )

    time.sleep(5)
    # wait for the VSCode window to open
    ok = wait_for_image('tempy.png', confidence=0.4)
    if not ok:
        close_window()
        return
    
    # Click on the VSCode window to ensure it's active
    pyautogui.click(x=1317, y=165)
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'g') # Open the "Go to Line" dialog in VSCode
    wait_for_image('linetogo.png', confidence=0.5)
    if start_line == 0:
        start_line = 1
    pyautogui.write(str(start_line), interval=0.2) # Write the line number to go to
    time.sleep(2)
    pyautogui.press('enter')  # Press Enter to go to the specified line
    
    time.sleep(2)
    # Select the line where Copilot should generate suggestions
    pyautogui.hotkey('ctrl', 'i')
    time.sleep(2)
    wait_for_image('ask.png')
    
    if num_lines == 1:
        prompt = f"Please complete a line of code here."  # this is prompt text
    else:
        prompt = f"Please complete {num_lines} lines of code here."
    pyautogui.write(prompt, interval=0.2) 
    raw = copy_all()

    # Check if the content was copied successfully
    if not raw:
        close_window()
        return
    ok = wait_for_image('bar.png', timeout=10, confidence=0.6)
    if not ok:
        close_window()
        return
    pyautogui.click(ok)
    time.sleep(2)
    pyautogui.press('enter')

    location = check_if_failed()
            
    if location:
        wait_time(3)
        close_window()
        return
    
    time.sleep(2)
    clipboard_content = copy_to_clipboard(raw)
    if not clipboard_content:
        close_window()
        wait_time(2)
        return
    
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
    # Copilot officially imposes a limit on the frequency of calls. 
    # Reducing the interval may result in an irreversible ban. 
    # Even with a 60-second sleep time, you should not generate continuously for an extended period.
    time.sleep(60)  # Wait for 60 seconds before processing the next file

    # close the VSCode window
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
            automate_vscode_interaction(file_path, filename, fold, model=model)
            nums += 1
            print(f"Processed {nums} files in {fold}")