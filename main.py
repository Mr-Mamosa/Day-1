import curses
from curses import wrapper
import time
import random
import textwrap
import csv
import datetime
import os

def start_screen(stdscr):
	"""
	Displays the main menu.
	Handles mode selection (15s, 30s, or Full Text).
	"""
	h, w = stdscr.getmaxyx()
	stdscr.clear()

	# Draw the "LazyVim" style branding
	title = " PAPAYAAA TYPING MASTER "
	stdscr.addstr(h // 4, (w // 2) - (len(title) // 2), title, curses.A_BOLD | curses.A_REVERSE)

	# Show your developer identity and version
	github = " github.com/Mr-Mamosa"
	version = "v1.0.0-stable"
	stdscr.addstr(h // 4 + 2, (w // 2) - (len(github) // 2), github, curses.color_pair(1))
	stdscr.addstr(h // 4 + 3, (w // 2) - (len(version) // 2), version, curses.A_DIM)

	# Panel for mode selection
	status_box = " [ STATUS: DEPLOYED / SELECT MODE ] "
	stdscr.addstr(h // 2 - 2, (w // 2) - (len(status_box) // 2), status_box, curses.color_pair(3))

	# Interactive Menu Options
	modes = [
		" (1) 15 Seconds   ",
		" (2) 30 Seconds   ",
		" (3) Full Paragraph ",
		" ──────────────── ",
		" <Esc>  Quit App  "
	]

	for i, line in enumerate(modes):
		stdscr.addstr(h // 2 + i, (w // 2) - (len(line) // 2), line)

	stdscr.refresh()

	# Logic to return the selected time limit to the main loop
	while True:
		key = stdscr.getkey()
		if key == '1': return 15
		if key == '2': return 30
		if key == '3': return None # Marathon Mode
		if key in ("\x1b", "KEY_EXIT"): exit()

def log_session_data(wpm, accuracy, text_len, time_taken):
	"""
	Saves the typing session to a CSV file.
	This builds your dataset for future Data Science / Regression analysis.
	"""
	file_name = 'typing_stats.csv'
	file_exists = os.path.isfile(file_name)

	with open(file_name, 'a', newline='') as f:
		writer = csv.writer(f)
		# Add headers if it's a new file
		if not file_exists:
			writer.writerow(['timestamp', 'wpm', 'accuracy', 'char_count', 'duration_sec'])

		writer.writerow([
			datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
			wpm, accuracy, text_len, round(time_taken, 2)
		])

def get_high_score():
	"""
	Scans the CSV file to find the highest WPM ever recorded.
	"""
	high_score = 0
	file_name = 'typing_stats.csv'
	if os.path.isfile(file_name):
		with open(file_name, 'r') as f:
			reader = csv.DictReader(f)
			for row in reader:
				# Convert wpm string to int and compare
				wpm_val = int(row['wpm'])
				if wpm_val > high_score:
					high_score = wpm_val
	return high_score


def display_text(stdscr, target, current, wpm=0, accuracy=100, time_left=None):
	"""
	Renders the actual game UI, including the text box,
	wrapped lines, and live stats.
	"""
	h, w = stdscr.getmaxyx()

	# Box dimensions (Responsive: 80% of terminal width)
	box_w = int(w * 0.8)
	padding = 2
	max_text_width = box_w - (padding * 2)

	# Wrap long text so it stays inside the box boundaries
	wrapped_target = textwrap.wrap(target, width=max_text_width)
	box_h = len(wrapped_target) + 4
	start_y, start_x = (h // 2) - (box_h // 2), (w // 2) - (box_w // 2)

	# UI: Optional Countdown Timer in the corner
	if time_left is not None:
		stdscr.addstr(start_y - 2, start_x, f" 󱑂 TIME LEFT: {time_left}s ", curses.color_pair(3) | curses.A_BOLD)

	# UI: Draw the Border (Using Unicode for that clean look)
	stdscr.attron(curses.color_pair(3))
	stdscr.addstr(start_y, start_x, "─" * box_w)
	stdscr.addstr(start_y + box_h, start_x, "─" * box_w)
	for i in range(1, box_h):
		stdscr.addstr(start_y + i, start_x, "│")
		stdscr.addstr(start_y + i, start_x + box_w, "│")
	stdscr.addstr(start_y, start_x, "┌")
	stdscr.addstr(start_y, start_x + box_w, "┐")
	stdscr.addstr(start_y + box_h, start_x, "└")
	stdscr.addstr(start_y + box_h, start_x + box_w, "┘")
	stdscr.addstr(start_y, start_x + 2, "  PaPaYaaa-Typing ", curses.A_BOLD)
	stdscr.attroff(curses.color_pair(3))

	# UI: Draw the Text and overlay the colors (Green = Right, Red = Wrong)
	current_char_idx = 0
	cursor_pos = (start_y + 2, start_x + padding)

	for row_idx, line in enumerate(wrapped_target):
		line_y = start_y + 2 + row_idx
		line_x = start_x + padding
		stdscr.addstr(line_y, line_x, line, curses.color_pair(3) | curses.A_DIM)

		for char_in_line_idx, target_char in enumerate(line):
			if current_char_idx < len(current):
				user_char = current[current_char_idx]
				color = curses.color_pair(1) if user_char == target_char else curses.color_pair(2)
				stdscr.addstr(line_y, line_x + char_in_line_idx, user_char, color)
				current_char_idx += 1

				# Move cursor to the next spot
				if current_char_idx == len(current):
					if char_in_line_idx == len(line) - 1 and row_idx < len(wrapped_target) - 1:
						cursor_pos = (line_y + 1, line_x) # Jump to next line
					else:
						cursor_pos = (line_y, line_x + char_in_line_idx + 1)
			elif current_char_idx == len(current):
				cursor_pos = (line_y, line_x + char_in_line_idx)
				break

	# UI: Bottom Dashboard for WPM and Accuracy
	stats = f"  {wpm} WPM | 󰓃 {accuracy}% "
	stdscr.addstr(start_y + box_h, start_x + 2, stats, curses.A_REVERSE)
	stdscr.move(cursor_pos[0], cursor_pos[1])

def load_text():
	"""
	Randomly picks a legal or technical text for the typing test.
	"""
	lines = [
		"Jean Watsons theory consists of four steps and can apply to the fields of scientific research and medicine alike...",
		"Sekmadienis Ltd. v. Lithuania concerned a lawsuit filed by the Lithuanian Government against the advertising company...",
		"The Communist Manifesto expresses Communist theories while Capital is a scholarly examination...",
		"As a dynamically developing industry, the healthcare system experiences several prominent challenges...",
		"Art and design are ways in which humans show a declaration of creativity and influence performance..."
	]
	return random.choice(lines)

def show_results(stdscr, wpm, accuracy, chars_typed):
	h, w = stdscr.getmaxyx()
	stdscr.erase()

	# Fetch the previous best before this session
	prev_best = get_high_score()
	is_new_record = wpm > prev_best

	title = " --- PERFORMANCE SUMMARY --- "
	stdscr.addstr(h // 4, (w // 2) - (len(title) // 2), title, curses.A_BOLD | curses.color_pair(3))

	# Highlight the WPM in green if it's a new record
	wpm_color = curses.color_pair(1) if is_new_record else curses.A_NORMAL
	stdscr.addstr(h // 2 - 2, (w // 2) - 10, f"Speed:    {wpm} WPM", wpm_color)

	if is_new_record:
		stdscr.addstr(h // 2 - 2, (w // 2) + 10, " 󰄬 NEW RECORD!", curses.color_pair(1) | curses.A_BOLD)
	else:
		stdscr.addstr(h // 2 - 1, (w // 2) - 10, f"Best:     {prev_best} WPM", curses.A_DIM)

	results = [
		f"Accuracy: {accuracy}%",
		f"Total Characters: {chars_typed}",
		"───────────────────────────",
		"Press any key to return to menu..."
	]

	for i, line in enumerate(results):
		# Start from offset 1 because we already drew the WPM lines
		stdscr.addstr(h // 2 + 1 + i, (w // 2) - (len(line) // 2), line)

	stdscr.refresh()
	stdscr.getkey()
def wpm_test(stdscr, time_limit):
	"""
	Main loop with 'Infinite Text' logic.
	If the user finishes a paragraph, a new one loads to keep the race going.
	"""
	target_text = load_text()
	currnt_text = []
	wpm = 0
	accuracy = 100
	start_time = None
	total_chars_accumulated = 0 # Tracks chars from previous finished paragraphs

	curses.curs_set(2)

	while True:
		# 1. Calculation Logic
		time_elapsed = max(time.time() - (start_time or time.time()), 0.1)
		# WPM formula updated to include accumulated characters
		wpm = round(((total_chars_accumulated + len(currnt_text)) / 5) / (time_elapsed / 60))

		# Handle the Countdown for 15s/30s modes
		time_left = None
		if time_limit and start_time:
			time_left = max(0, time_limit - int(time_elapsed))
		elif time_limit:
			time_left = time_limit

		# Accuracy calculation
		correct_chars = sum(1 for i, c in enumerate(currnt_text) if c == target_text[i])
		if len(currnt_text) > 0:
			accuracy = round((correct_chars / len(currnt_text)) * 100, 1)

		# 2. UI Rendering
		stdscr.erase()
		display_text(stdscr, target_text, currnt_text, wpm, accuracy, time_left)
		stdscr.refresh()

		# 3. Infinite Text Logic:
		# If current text is done but time remains, swap in a new paragraph
		if len(currnt_text) == len(target_text) and (time_left is None or time_left > 0):
			total_chars_accumulated += len(currnt_text)
			target_text = load_text() # Pull fresh paragraph
			currnt_text = [] # Clear the input buffer for the new text
			continue

		# 4. Completion/End Check
		# Ends if timer hits zero OR if Marathon mode (None) finishes the text
		if (time_limit and time_left == 0) or (time_limit is None and len(currnt_text) == len(target_text)):
			stdscr.nodelay(False)
			total_final_chars = total_chars_accumulated + len(currnt_text)

			# Save to CSV for Data Science analysis
			log_session_data(wpm, accuracy, total_final_chars, time_elapsed)

			# Show the new Results screen
			show_results(stdscr, wpm, accuracy, total_final_chars)
			break

		# 5. Input Handling
		try:
			key = stdscr.getkey()
		except:
			time.sleep(0.01) # Keeps CPU usage low on Arch
			continue

		if start_time is None:
			start_time = time.time()
			stdscr.nodelay(True)

		if key in ("\x1b", "KEY_EXIT"): # ESC to quit
			break

		if key in ("KEY_BACKSPACE", '\b', '\x7f'):
			if len(currnt_text) > 0:
				currnt_text.pop()
		elif len(key) == 1:
			if len(currnt_text) < len(target_text):
				currnt_text.append(key)

def main(stdscr):
	"""
	Entry point. Initializes colors and runs the main application loop.
	"""
	curses.start_color()
	curses.use_default_colors()

	# Catppuccin Mocha Color Palette
	curses.init_pair(1, 114, -1) # Success (Green)
	curses.init_pair(2, 210, -1) # Error (Red)
	curses.init_pair(3, 183, -1) # UI Border (Mauve)

	while True:
		mode = start_screen(stdscr)
		wpm_test(stdscr, mode)

if __name__ == "__main__":
	wrapper(main)
