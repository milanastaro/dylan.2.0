import streamlit as st
import time
import numpy as np
import random

# ---------------- Game Config ----------------
GRID_SIZE = 20
CELL_SIZE = 20

def init_game():
    st.session_state.snake = [(5, 5)]
    st.session_state.food = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
    st.session_state.direction = (0, 1)
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.manual = True

def draw_board():
    board = np.zeros((GRID_SIZE, GRID_SIZE, 3), dtype=np.uint8)
    for x, y in st.session_state.snake:
        board[y, x] = [0, 255, 0]  # Snake green
    fx, fy = st.session_state.food
    board[fy, fx] = [255, 0, 0]    # Food red
    return board

def move_snake():
    head_x, head_y = st.session_state.snake[-1]
    dx, dy = st.session_state.direction
    new_head = (head_x + dx, head_y + dy)

    if (new_head in st.session_state.snake or
        not 0 <= new_head[0] < GRID_SIZE or
        not 0 <= new_head[1] < GRID_SIZE):
        st.session_state.game_over = True
        return

    st.session_state.snake.append(new_head)

    if new_head == st.session_state.food:
        st.session_state.food = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        st.session_state.score += 1
    else:
        st.session_state.snake.pop(0)

def ai_decision():
    # Simple greedy AI to chase food
    head_x, head_y = st.session_state.snake[-1]
    food_x, food_y = st.session_state.food
    dx = np.sign(food_x - head_x)
    dy = np.sign(food_y - head_y)
    if abs(food_x - head_x) > abs(food_y - head_y):
        return (dx, 0)
    else:
        return (0, dy)

def manual_controls():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⬅️"):
            st.session_state.direction = (-1, 0)
    with c2:
        if st.button("⬆️"):
            st.session_state.direction = (0, -1)
    with c3:
        if st.button("⬇️"):
            st.session_state.direction = (0, 1)
    with c4:
        if st.button("➡️"):
            st.session_state.direction = (1, 0)

# ---------------- Streamlit App ----------------
st.title("🐍 AI Snake Game")

if 'snake' not in st.session_state:
    init_game()

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("Restart Game"):
        init_game()

    st.session_state.manual = st.checkbox("Manual Controls", value=True)
    st.write(f"Score: {st.session_state.score}")

with col1:
    board = draw_board()
    st.image(board, width=GRID_SIZE*CELL_SIZE)

    if st.session_state.manual:
        manual_controls()
    else:
        st.session_state.direction = ai_decision()

    if not st.session_state.game_over:
        move_snake()
        time.sleep(0.2)
        st.experimental_rerun()
    else:
        st.error("Game Over!")
