import random

MOOD_POOLS = {
"angry":[
("Animal Helper","Puzzle","Match each animal with a safe place.","2 min","memory"),
("Smash the Stress","Arcade","Tap the targets to release a little tension.","1 min","target_blitz"),
("Color Cooldown","Focus","Find the color that matches the prompt.","1 min","color_clash"),
("Count Back","Focus","Answer quick countdown prompts at your own pace.","1 min","math_sprint"),
("Gentle Rescue","Puzzle","Remember and match friendly pairs.","2 min","memory"),
("Target Blitz","Arcade","Hit as many targets as you can before time runs out.","30 sec","target_blitz"),
("Calm Countdown","Focus","Solve simple numbers while slowing down.","1 min","math_sprint"),
("Reaction Reset","Arcade","Wait for the signal, then react quickly.","30 sec","reaction_rush"),
],
"sad":[
("Tiny Garden","Memory","Match pairs and build a tiny mental garden.","2 min","memory"),
("Memory Match","Memory","Find all matching pairs.","2 min","memory"),
("Cloud Catcher","Arcade","Catch the gentle falling clouds.","30 sec","brain_tap"),
("Kind Words","Word","Unscramble a kind word.","1 min","word_scramble"),
("Warm Light","Focus","Find the odd color and keep your attention gentle.","1 min","odd_one_out"),
("Slow Tap","Arcade","Tap only when the circle is ready.","30 sec","reaction_rush"),
],
"stressed":[
("Calm Countdown","Focus","Solve simple sums without rushing.","1 min","math_sprint"),
("Breathing Challenge","Focus","Follow a slow rhythm and keep your score steady.","1 min","brain_tap"),
("Color Flow","Focus","Match colors one step at a time.","1 min","color_clash"),
("Slow Maze","Puzzle","Use memory to find matching paths.","2 min","memory"),
("Rain Room","Focus","Tap the calm signals as they appear.","30 sec","reaction_rush"),
("Gentle Numbers","Focus","Recall a short number sequence.","1 min","number_recall"),
],
"confused":[
("Pattern Rush","Puzzle","Remember and repeat a short pattern.","1 min","pattern_rush"),
("Number Recall","Memory","Remember the number shown briefly.","1 min","number_recall"),
("Calm Drive","Focus","Choose the matching color calmly.","1 min","color_clash"),
("Odd One Out","Puzzle","Spot the one different tile.","1 min","odd_one_out"),
("Sorting Puzzle","Puzzle","Use quick math choices to sort the prompts.","1 min","math_sprint"),
],
"bored":[
("Brain Rot Tap","Arcade","Tap as many circles as you can.","30 sec","brain_tap"),
("Reaction Rush","Arcade","React when the signal appears.","30 sec","reaction_rush"),
("Color Clash","Focus","Match the target color before time runs out.","30 sec","color_clash"),
("Word Scramble","Word","Unscramble as many words as you can.","1 min","word_scramble"),
("Math Sprint","Brain","Solve quick sums.","1 min","math_sprint"),
("Pattern Rush","Puzzle","Repeat patterns before they disappear.","1 min","pattern_rush"),
],
"lonely":[
("Tic-Tac-Toe","Social","Play a quick match against a friend or the computer.","2 min","tic_tac_toe"),
("Rock Paper Scissors","Social","Play a quick best-of-five duel.","1 min","rps"),
("Quick Duel","Arcade","Challenge your reaction speed.","30 sec","reaction_rush"),
("Story Chain","Word","Build a tiny word chain in your head.","1 min","word_scramble"),
("Friendly Challenge","Arcade","See how many targets you can catch.","30 sec","target_blitz"),
],
"tired":[
("Gentle Stretch","Focus","A simple slow-tap activity with no pressure.","30 sec","brain_tap"),
("Slow Tap","Arcade","Tap gently and follow the signal.","30 sec","reaction_rush"),
("Simple Memory","Memory","Find a few easy matching pairs.","1 min","memory"),
("Calm Count","Focus","Solve a few easy number prompts.","1 min","math_sprint"),
("Hydration Reminder","Focus","Take a short pause and complete a simple color round.","30 sec","color_clash"),
],
"anxious":[
("Breathing Challenge","Focus","Follow a gentle visual rhythm with simple taps.","1 min","brain_tap"),
("Slow Maze","Puzzle","Use a calm memory challenge.","2 min","memory"),
("Color Flow","Focus","Match the target color at a comfortable pace.","1 min","color_clash"),
("Calm Countdown","Focus","Answer simple questions without racing.","1 min","math_sprint"),
("Warm Light","Focus","Spot the small difference in a relaxed round.","1 min","odd_one_out"),
],
"happy":[
("Reaction Rush","Arcade","Test your reaction speed.","30 sec","reaction_rush"),
("Color Clash","Focus","Match colors quickly.","30 sec","color_clash"),
("Brain Rot Tap","Arcade","Tap as many targets as possible.","30 sec","brain_tap"),
("Word Scramble","Word","Unscramble quick words.","1 min","word_scramble"),
("Quick Challenge","Arcade","Hit the targets before time runs out.","30 sec","target_blitz"),
("Pattern Rush","Puzzle","Repeat increasingly tricky patterns.","1 min","pattern_rush"),
],
"neutral":[
("Memory Match","Memory","Find matching pairs.","2 min","memory"),
("Reaction Rush","Arcade","React to the signal.","30 sec","reaction_rush"),
("Color Clash","Focus","Match the target color.","30 sec","color_clash"),
("Math Sprint","Brain","Solve quick sums.","1 min","math_sprint"),
("Word Scramble","Word","Unscramble a word.","1 min","word_scramble"),
("Pattern Rush","Puzzle","Repeat a short pattern.","1 min","pattern_rush"),
]
}

def seed_activities(conn):
    count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    if count >= 100:
        return
    conn.execute("DELETE FROM activities")
    rows = []
    for mood, base in MOOD_POOLS.items():
        for i in range(10):
            for name, cat, desc, dur, game in base:
                if len(rows) >= 100:
                    break
                suffix = "" if i == 0 else f" • Round {i+1}"
                rows.append((name + suffix, mood, cat, desc, dur, game))
            if len(rows) >= 100:
                break
    conn.executemany(
        "INSERT INTO activities(name,mood,category,description,duration,game_key) VALUES(?,?,?,?,?,?)",
        rows[:100]
    )
    conn.commit()

def get_recommendations(conn, mood, count=6):
    rows = conn.execute("SELECT * FROM activities WHERE mood=?", (mood,)).fetchall()
    rows = list(rows)
    random.shuffle(rows)
    return [dict(x) for x in rows[:count]]
