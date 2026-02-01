import curses
from curses import wrapper

def start_screen(stdscr):
  stdscr.clear()
  stdscr.addstr("Welcome to the PaPaYaaa TypingGame!")
  stdscr.addstr("\nPress any key to begin!")
  stdscr.refresh()
  stdscr.getkey()

def wpm_test(stdscr):
  target_text = "Wassup gang this is the sample text that you are going to use for you test, go and Fuck yourself."
  currnt_text = []

  while True:
    stdscr.clear()
    stdscr.addstr(target_text)

    for char in currnt_text:
      stdscr.addstr(char,curses.color_pair(1))

    stdscr.refresh()
    key = stdscr.getkey()

    if ord(key) == 27:
      break

    if key in ("KEY_BACKSPACE","\b","\x7f"):
      if len(key) == 1 and ord(key) == 27:
        break
      if len(currnt_text) > 0:
        currnt_text.pop()
      else:
        currnt_text.append(key)

    currnt_text.append(key)
def main(stdscr):
  curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
  curses.init_pair(2,curses.COLOR_RED,curses.COLOR_BLACK)
  curses.init_pair(3,curses.COLOR_WHITE,curses.COLOR_BLACK)

  start_screen(stdscr)
  wpm_test(stdscr)
wrapper(main)
