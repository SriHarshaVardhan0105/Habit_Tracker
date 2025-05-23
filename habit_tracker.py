# Habit Tracker App using Streamlit
import streamlit as st
import datetime
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

# File to store user data
DATA_FILE = "habit_data.json"

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Calculate streak and completion
def calculate_streak(dates):
    today = datetime.date.today()
    streak = 0
    while str(today) in dates:
        streak += 1
        today -= datetime.timedelta(days=1)
    return streak

def calculate_completion(dates):
    if not dates:
        return 0
    first_day = datetime.datetime.strptime(min(dates), "%Y-%m-%d").date()
    total_days = (datetime.date.today() - first_day).days + 1
    return round(len(dates) / total_days * 100, 2) if total_days > 0 else 0

# Get longest streak
def get_longest_streak(dates):
    if not dates:
        return []
    sorted_dates = sorted(datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates)
    longest = []
    current = [sorted_dates[0]]
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            current.append(sorted_dates[i])
        else:
            if len(current) > len(longest):
                longest = current[:]
            current = [sorted_dates[i]]
    if len(current) > len(longest):
        longest = current
    return set(longest)

# Plot progress
def plot_progress(dates):
    if not dates:
        return
    date_objs = [datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates]
    counts = {}
    for d in date_objs:
        counts[d] = counts.get(d, 0) + 1
    dates_sorted = sorted(counts.items())
    x = [d[0] for d in dates_sorted]
    y = [d[1] for d in dates_sorted]
    sns.set_style("whitegrid")
    plt.figure(figsize=(8, 4))
    plt.plot(x, y, marker='o')
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Habits Done")
    plt.title("Habit Progress Over Time")
    st.pyplot(plt)

# Calendar view with month navigation and longest streak highlight
def show_calendar(dates, habit_name):
    st.subheader("📅 Calendar View")
    dates_set = set(dates)
    longest_streak = get_longest_streak(dates)
    today = datetime.date.today()
    month_offset = st.slider(
        "Select month offset (0 = current month)",
        -12, 12, 0,
        key=f"month_offset_{habit_name}"
    )
    year, month = (today + datetime.timedelta(days=month_offset * 30)).year, (today + datetime.timedelta(days=month_offset * 30)).month
    cal = calendar.monthcalendar(year, month)
    st.markdown(f"**{calendar.month_name[month]} {year}**")
    cal_display = "| Mon | Tue | Wed | Thu | Fri | Sat | Sun |\n|------|------|------|------|------|------|------|"
    for week in cal:
        row = "|"
        for day in week:
            if day == 0:
                row += "      |"
            else:
                date_obj = datetime.date(year, month, day)
                date_str = str(date_obj)
                if date_obj in longest_streak:
                    row += f" 🌟{str(day).rjust(2)} |"
                elif date_str in dates_set:
                    row += f" ✅{str(day).rjust(2)} |"
                else:
                    row += f"  {str(day).rjust(2)} |"
        cal_display += "\n" + row
    st.markdown(cal_display)

# Show badges based on streaks
def show_achievements(streak):
    if streak >= 30:
        st.success("🏅 30-Day Streak Champion!")
    elif streak >= 14:
        st.info("🥈 2-Week Warrior!")
    elif streak >= 7:
        st.info("🥉 7-Day Starter Streak!")

# Streamlit UI
st.title("🌱 Habit Tracker")

# Login system
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button:
    if username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
    else:
        st.sidebar.warning("Please enter both username and password.")

if st.session_state.get("logged_in"):
    data = load_data()
    user_data = data.get(st.session_state.username, {})
    habits = list(user_data.keys())

    st.success(f"Welcome, {st.session_state.username}!")

    new_habit = st.text_input("Add a new habit:")
    if st.button("Add Habit") and new_habit:
        if new_habit not in habits:
            user_data[new_habit] = []
            habits.append(new_habit)
            st.success(f"Habit '{new_habit}' added!")
        else:
            st.warning("Habit already exists.")

    if habits:
        remove_habit = st.selectbox("Remove a habit:", habits)
        if st.button("Remove Habit") and remove_habit:
            if remove_habit in user_data:
                del user_data[remove_habit]
                habits.remove(remove_habit)
                st.success(f"Habit '{remove_habit}' removed!")

    today = str(datetime.date.today())
    for habit in habits:
        st.markdown(f"### ✅ {habit}")
        done_today = today in user_data[habit]
        if st.checkbox("Mark as done today", value=done_today, key=habit):
            if not done_today:
                user_data[habit].append(today)
        else:
            if done_today:
                user_data[habit].remove(today)
        streak = calculate_streak(user_data[habit])
        completion = calculate_completion(user_data[habit])
        st.write(f"🔥 Streak: {streak} days")
        show_achievements(streak)
        st.write(f"📊 Completion: {completion}%")
        plot_progress(user_data[habit])
        show_calendar(user_data[habit], habit)

    data[st.session_state.username] = user_data
    save_data(data)
else:
    st.warning("Please login from the sidebar to continue.")