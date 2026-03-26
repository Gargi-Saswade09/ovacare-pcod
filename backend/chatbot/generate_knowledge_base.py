import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "chatbot_knowledge.json")

entries = []

def add(topic, title, category, keywords, content):
    entries.append({
        "topic": topic,
        "title": title,
        "category": category,
        "keywords": keywords,
        "content": content
    })

pcod_items = [
    ("pcod_management", "Managing PCOD step by step", "pcod_general", ["pcod", "manage", "control", "reduce", "cure", "get rid"], "PCOD is usually managed rather than instantly removed. Helpful steps include regular exercise, balanced meals with protein and fiber, good sleep, weight management when needed, and guidance from a gynecologist. The goal is to control symptoms and improve hormonal balance over time."),
    ("pcod_can_it_be_cured", "Can PCOD be cured", "pcod_general", ["pcod", "cured", "cure", "gone", "permanent"], "PCOD often improves with lifestyle changes and medical guidance, but it is better to think in terms of management and symptom control rather than an instant cure. Many people feel much better when routines become consistent."),
    ("pcod_symptoms_overview", "Common symptoms of PCOD", "pcod_general", ["pcod", "symptoms", "signs", "periods", "acne"], "Common PCOD symptoms can include irregular periods, acne, weight changes, unwanted hair growth, scalp hair thinning, and difficulty managing energy. A doctor can confirm the cause because symptoms can overlap with other conditions."),
    ("pcod_irregular_periods", "PCOD and irregular periods", "pcod_general", ["pcod", "irregular periods", "cycle", "missed periods"], "Irregular periods are common in PCOD because hormone patterns may affect ovulation. Tracking your cycle and discussing major changes with a doctor can be helpful."),
    ("pcod_weight_gain", "PCOD and weight gain", "pcod_general", ["pcod", "weight gain", "weight", "belly fat"], "Some people with PCOD find weight management harder because hormones and insulin response may change. Steady habits like walking, strength training, balanced meals, and sleep are usually more helpful than crash diets."),
    ("pcod_acne", "PCOD and acne", "pcod_general", ["pcod", "acne", "skin", "pimples"], "Acne can happen in PCOD because hormonal shifts may affect the skin. Supportive habits include regular skincare, balanced meals, good sleep, and doctor guidance if acne is severe."),
    ("pcod_hair_growth", "PCOD and extra hair growth", "pcod_general", ["pcod", "hair growth", "facial hair", "hirsutism"], "Extra hair growth on the face or body can happen in PCOD. A healthcare professional can explain treatment options and help you choose a plan that feels manageable."),
    ("pcod_hair_loss", "PCOD and hair fall", "pcod_general", ["pcod", "hair loss", "hair fall", "thinning"], "Some people with PCOD notice scalp hair thinning or extra hair fall. Stress, nutrition, and hormones can all play a role, so balanced routines and medical advice can help."),
    ("pcod_diagnosis", "How PCOD is diagnosed", "pcod_general", ["pcod", "diagnosis", "test", "doctor"], "PCOD is usually assessed using symptoms, cycle history, physical signs, and sometimes lab tests or imaging. A gynecologist or endocrinologist can guide the process."),
    ("pcod_lifestyle", "Lifestyle basics for PCOD", "pcod_general", ["pcod", "lifestyle", "routine", "habits"], "A helpful PCOD routine often includes regular meals, movement most days, enough sleep, lower stress, and follow-up with a doctor when symptoms are bothering you."),
    ("pcod_sleep", "Why sleep matters in PCOD", "pcod_general", ["pcod", "sleep", "late nights", "rest"], "Good sleep supports hormone balance, appetite control, and stress management. Try sleeping and waking around the same time each day."),
    ("pcod_stress_link", "PCOD and stress connection", "pcod_general", ["pcod", "stress", "hormones", "mental load"], "Stress does not directly cause PCOD, but high stress can make routines harder and may worsen symptoms like poor sleep, cravings, and low energy. Stress support is a useful part of PCOD care."),
    ("pcod_insulin_general", "PCOD and insulin response", "pcod_general", ["pcod", "insulin", "sugar", "energy"], "Some people with PCOD have changes in insulin response, which can affect hunger, weight, and energy. Balanced meals with protein and fiber may help support steadier energy."),
    ("pcod_doctor_support", "When to see a doctor for PCOD", "pcod_general", ["pcod", "doctor", "gynecologist", "when to seek help"], "See a doctor if periods are very irregular, symptoms are getting worse, acne or hair loss is severe, or you feel confused about what to do next. Professional guidance can make management easier."),
    ("pcod_tracking", "Tracking symptoms in PCOD", "pcod_general", ["pcod", "track", "journal", "symptoms"], "Tracking periods, acne, sleep, stress, exercise, and meals can help you notice patterns. This can also make doctor visits more useful."),
    ("pcod_food_timing", "Meal timing for PCOD", "pcod_general", ["pcod", "meal timing", "skip meals", "eating routine"], "For many people with PCOD, regular meals work better than skipping and overeating later. A steady eating pattern may help with energy and cravings."),
    ("pcod_small_changes", "Small changes that help PCOD", "pcod_general", ["pcod", "small steps", "start", "beginner"], "Start small: a daily walk, more water, a protein-rich breakfast, and less sugary snacking. Tiny consistent steps often work better than trying to change everything at once."),
    ("pcod_realistic_expectations", "What improvement in PCOD looks like", "pcod_general", ["pcod", "improve", "better", "results"], "Improvement in PCOD often looks like better energy, more regular habits, fewer cravings, or easier symptom control over time. Progress is usually gradual, not instant."),
    ("pcod_hormone_balance", "Supporting hormone balance in PCOD", "pcod_general", ["pcod", "hormone balance", "balance hormones"], "Helpful habits for hormone balance include enough sleep, regular movement, balanced meals, stress management, and staying consistent with medical advice."),
    ("pcod_reassurance", "PCOD reassurance", "pcod_general", ["pcod", "worried", "scared", "new diagnosis"], "Feeling worried about PCOD is understandable. Many people manage it well with a practical routine, patience, and support from a doctor.")
]

stress_items = [
    ("stress_immediate_help", "What to do when stressed right now", "stress_general", ["stressed", "right now", "calm", "relax", "overwhelmed"], "If you feel stressed right now, pause for a minute, take slow deep breaths, drink water, sit in a quiet place, and focus on one small step instead of everything at once. A short walk or gentle stretching can also help reduce stress in the moment."),
    ("stress_overwhelmed", "What to do when feeling overwhelmed", "stress_general", ["overwhelmed", "too much", "pressure", "stressed"], "When everything feels like too much, pick just one tiny next step, such as drinking water, writing a short to-do list, or standing up and stretching. Reducing the size of the task can calm the mind."),
    ("stress_sleep", "Sleep and stress", "stress_general", ["sleep", "stress", "rest", "insomnia"], "Poor sleep can make stress feel stronger. Try a simple bedtime routine, reduce screen time before sleep, and avoid too much caffeine late in the day."),
    ("stress_breathing", "Breathing for stress relief", "stress_general", ["stress", "breathing", "calm", "panic"], "Slow breathing can help when stress rises. Inhale gently, exhale a little longer than the inhale, and repeat for a few minutes without forcing it."),
    ("stress_study_pressure", "Stress from studies", "stress_general", ["study", "exam", "college", "pressure"], "Study stress can feel intense. Try short study blocks, one clear priority at a time, quick stretch breaks, and enough sleep so the brain can recover."),
    ("stress_work_pressure", "Stress from daily workload", "stress_general", ["work", "tasks", "pressure", "busy"], "When workload feels heavy, sort tasks into urgent, important, and later. Finishing one small task can help lower the feeling of chaos."),
    ("stress_feeling_low", "Feeling low and stressed", "stress_general", ["low", "down", "stressed", "tired"], "Feeling low can happen when stress builds up. Gentle routines like breathing, sunlight, talking to someone you trust, and eating regular meals may help you feel steadier."),
    ("stress_anxious", "Feeling anxious", "stress_general", ["anxious", "restless", "worry", "nervous"], "Anxiety can make the body feel restless and the mind race. Grounding yourself with slow breathing, a calm space, and one small action can help in the moment."),
    ("stress_body_signals", "Body signs of stress", "stress_general", ["stress", "body", "headache", "tension"], "Stress can show up as headaches, neck tension, poor sleep, low energy, or trouble focusing. These signs are a reminder to slow down and care for your routine."),
    ("stress_talk_support", "Talking to someone when stressed", "stress_general", ["stress", "talk", "support", "friend"], "Sharing stress with a trusted friend, family member, counselor, or teacher can reduce the burden. You do not have to handle everything alone."),
    ("stress_routine", "A simple anti-stress routine", "stress_general", ["stress", "routine", "daily", "habits"], "A practical anti-stress routine can include enough water, movement, regular meals, sleep, short breathing breaks, and less multitasking."),
    ("stress_morning_reset", "Morning reset for stress", "stress_general", ["stress", "morning", "start day", "reset"], "A calmer morning can help the whole day. Try sunlight, water, a balanced breakfast, and one simple plan for the day instead of rushing into everything."),
    ("stress_evening_reset", "Evening reset for stress", "stress_general", ["stress", "evening", "night", "wind down"], "At night, try dimmer lights, less scrolling, light stretching, and a fixed sleep time. A calm evening can make stress feel more manageable."),
    ("stress_food_link", "Food and stress connection", "stress_general", ["stress", "food", "cravings", "energy"], "Stress can affect appetite and cravings. Eating regular balanced meals can help avoid the energy crashes that make stress feel worse."),
    ("stress_breaks", "Why breaks help stress", "stress_general", ["stress", "break", "rest", "pause"], "Short breaks improve focus and reduce mental overload. Even a few minutes away from the screen or task can help your mind reset."),
    ("stress_movement", "Movement and stress relief", "stress_general", ["stress", "walk", "movement", "exercise"], "Light movement like walking or stretching can reduce physical tension and improve mood. It does not need to be intense to be useful."),
    ("stress_journaling", "Journaling for stress", "stress_general", ["stress", "journal", "writing", "thoughts"], "Writing down worries or next steps can make thoughts feel less crowded. A short journal entry can help you sort what is in your control."),
    ("stress_social_media", "Stress and social media", "stress_general", ["stress", "social media", "phone", "compare"], "Too much scrolling can increase stress for some people. A short break from social media, especially before bed, may help you feel calmer."),
    ("stress_seek_help", "When to get help for stress", "stress_general", ["stress", "help", "counselor", "doctor"], "Get extra support if stress is stopping you from sleeping, eating, studying, or feeling safe. A counselor, doctor, or trusted adult can help you make a plan."),
    ("stress_reassurance", "Stress reassurance", "stress_general", ["stress", "worried", "normal", "support"], "Stress does not mean you are weak. It means your mind and body need support, rest, and a practical plan.")
]

diet_pcod_items = [
    ("diet_pcod_basics", "Diet basics for PCOD", "diet_pcod", ["pcod", "diet", "food", "meal"], "A practical PCOD diet focuses on vegetables, fruits, whole grains, dal, eggs, paneer, tofu, curd, nuts, and seeds. Try to include protein and fiber in meals."),
    ("diet_pcod_breakfast", "Breakfast ideas for PCOD", "diet_pcod", ["pcod", "breakfast", "oats", "eggs"], "Good PCOD breakfast ideas include oats with seeds, eggs with roti, curd with nuts, paneer with vegetables, or dal chilla. The goal is a meal with protein and fiber."),
    ("diet_pcod_lunch", "Lunch ideas for PCOD", "diet_pcod", ["pcod", "lunch", "meal", "plate"], "A simple PCOD lunch can be dal or chicken or paneer with vegetables and rice or roti. Try to make half the plate vegetables, one part protein, and one part whole grains."),
    ("diet_pcod_dinner", "Dinner ideas for PCOD", "diet_pcod", ["pcod", "dinner", "night meal"], "A useful PCOD dinner can include vegetables with dal, paneer, tofu, fish, or eggs plus roti or a moderate portion of rice. Try not to keep dinner very heavy or very late."),
    ("diet_pcod_snacks", "Snack ideas for PCOD", "diet_pcod", ["pcod", "snacks", "hunger", "healthy snack"], "Good PCOD snacks include fruit with nuts, roasted chana, curd, sprouts, boiled eggs, or a small homemade sandwich with protein."),
    ("diet_pcod_avoid", "Foods to reduce in PCOD", "diet_pcod", ["pcod", "avoid", "junk", "sugar"], "Try to reduce sugary drinks, frequent bakery items, highly processed snacks, and oversized late-night meals. The goal is steadier energy, not perfection."),
    ("diet_pcod_sugar", "Sugar and PCOD", "diet_pcod", ["pcod", "sugar", "sweet", "dessert"], "Too many sugary foods can make energy rise and drop quickly. It often helps to keep sweets occasional and pair food with protein or fiber."),
    ("diet_pcod_hydration", "Water and PCOD", "diet_pcod", ["pcod", "water", "hydration", "drink"], "Water supports energy, digestion, and routine. Keeping a bottle nearby can make hydration easier during the day."),
    ("diet_pcod_protein", "Why protein helps in PCOD", "diet_pcod", ["pcod", "protein", "eggs", "paneer"], "Protein can help you feel fuller and support steadier energy. Try adding eggs, dal, paneer, tofu, curd, chicken, or fish to meals."),
    ("diet_pcod_fiber", "Why fiber helps in PCOD", "diet_pcod", ["pcod", "fiber", "vegetables", "whole grains"], "Fiber from vegetables, fruits, oats, dal, beans, and whole grains can support digestion and help meals feel more balanced."),
    ("diet_pcod_cravings", "Handling cravings in PCOD", "diet_pcod", ["pcod", "cravings", "snacking", "hungry"], "Cravings can feel stronger when meals are skipped or too low in protein. Regular meals and balanced snacks may help reduce this."),
    ("diet_pcod_indian_food", "Indian foods for PCOD", "diet_pcod", ["pcod", "indian food", "roti", "dal"], "Many home-style Indian foods can fit a PCOD-friendly pattern, such as dal, sabzi, roti, curd, sprouts, eggs, paneer, and fruit. Home-cooked balanced meals are often enough."),
    ("diet_pcod_weight_management", "Diet for PCOD and weight management", "diet_pcod", ["pcod", "weight loss", "diet", "manage weight"], "For PCOD and weight management, focus on regular meals, enough protein, more vegetables, fewer sugary drinks, and steady activity. Extreme restriction usually backfires."),
    ("diet_pcod_simple_plate", "Simple plate method for PCOD", "diet_pcod", ["pcod", "plate", "meal plan", "easy"], "An easy PCOD plate is half vegetables, one quarter protein, and one quarter whole grains. This keeps meals simple and practical."),
    ("diet_pcod_realistic", "Realistic diet advice for PCOD", "diet_pcod", ["pcod", "diet", "realistic", "start"], "You do not need a perfect diet. A realistic plan with regular meals, more home food, more protein, and fewer processed snacks can still help a lot.")
]

diet_stress_items = [
    ("diet_stress_basics", "Food basics for stress support", "diet_stress", ["stress", "diet", "food", "calm"], "Stress-supportive eating usually means regular meals, enough water, fruit, vegetables, protein, and fewer energy crashes from too much caffeine or sugar."),
    ("diet_stress_breakfast", "Breakfast for stressful days", "diet_stress", ["stress", "breakfast", "morning", "energy"], "On stressful days, a simple breakfast with protein and carbs, like eggs and toast, oats and nuts, or curd and fruit, may help keep energy steadier."),
    ("diet_stress_snacks", "Snacks that support stress recovery", "diet_stress", ["stress", "snacks", "food", "energy"], "Helpful snacks can include fruit with nuts, curd, roasted chana, or a small sandwich. Balanced snacks are often better than only sweet foods."),
    ("diet_stress_caffeine", "Caffeine and stress", "diet_stress", ["stress", "caffeine", "coffee", "tea"], "Too much caffeine can make some people feel more shaky, restless, or anxious. If stress is high, reducing caffeine may help."),
    ("diet_stress_hydration", "Water and stress", "diet_stress", ["stress", "water", "hydration", "tired"], "Not drinking enough water can make headaches, tiredness, and poor focus worse. Keep hydration simple and regular."),
    ("diet_stress_regular_meals", "Why regular meals help stress", "diet_stress", ["stress", "regular meals", "skip meals", "energy"], "Skipping meals can make you feel more tired and irritable. Regular meals may help reduce the stress that comes from low energy."),
    ("diet_stress_sugar", "Sugar and stress", "diet_stress", ["stress", "sugar", "sweet", "crash"], "Sugary foods may give a quick boost and then a crash. Balanced meals with protein and fiber often feel better over time."),
    ("diet_stress_comfort_food", "Comfort food and stress", "diet_stress", ["stress", "comfort food", "emotional eating"], "Comfort foods are normal sometimes, but if stress eating happens often, try pairing comfort foods with filling options like protein, fruit, or yogurt instead of judging yourself."),
    ("diet_stress_night", "Eating at night during stress", "diet_stress", ["stress", "night eating", "late food"], "Late-night eating sometimes happens when the day feels overwhelming. Regular meals earlier in the day may make evenings feel easier."),
    ("diet_stress_mood_food", "Foods that support mood", "diet_stress", ["stress", "mood", "food", "healthy"], "Balanced meals with fruits, vegetables, nuts, seeds, curd, oats, dal, and enough protein can support overall energy and mood."),
    ("diet_stress_simple", "Simple food ideas when stressed", "diet_stress", ["stress", "simple food", "easy meals"], "When stress is high, keep food simple: curd and fruit, eggs and toast, dal and rice, nuts and a banana, or soup with roti."),
    ("diet_stress_no_appetite", "When stress reduces appetite", "diet_stress", ["stress", "no appetite", "not hungry"], "If stress lowers your appetite, start small with easy foods like curd, fruit, soup, toast, or a smoothie. Small meals are okay."),
    ("diet_stress_overeating", "When stress leads to overeating", "diet_stress", ["stress", "overeating", "snacking", "binge"], "Stress can make overeating more likely. Regular meals, hydration, sleep, and reducing all-or-nothing dieting may help."),
    ("diet_stress_balanced_plate", "Balanced plate for stress", "diet_stress", ["stress", "plate", "meal", "balanced"], "A balanced plate can include vegetables, a protein source, and a carb source. Simple structure can help when your mind feels busy."),
    ("diet_stress_realistic", "Realistic diet advice for stress", "diet_stress", ["stress", "diet", "realistic", "small steps"], "During stressful times, aim for good-enough food instead of perfect food. Eating something balanced is usually better than skipping meals.")
]

exercise_pcod_items = [
    ("exercise_pcod_basics", "Exercise basics for PCOD", "exercise_pcod", ["pcod", "exercise", "workout", "walk"], "For PCOD, a sustainable routine often works best: brisk walking most days plus strength training two to three times a week."),
    ("exercise_pcod_beginner", "Beginner exercise for PCOD", "exercise_pcod", ["pcod", "beginner", "start exercise", "new"], "If you are just starting, begin with 15 to 20 minutes of walking and simple bodyweight exercises. Consistency matters more than intensity."),
    ("exercise_pcod_walking", "Walking for PCOD", "exercise_pcod", ["pcod", "walking", "steps", "cardio"], "Walking is a useful and simple exercise for PCOD. A daily brisk walk can support energy, routine, and weight management."),
    ("exercise_pcod_strength", "Strength training for PCOD", "exercise_pcod", ["pcod", "strength", "weights", "gym"], "Strength training can be helpful in PCOD because it supports muscle health and overall fitness. Two to three sessions a week is a practical starting point."),
    ("exercise_pcod_yoga", "Yoga for PCOD", "exercise_pcod", ["pcod", "yoga", "stretch", "calm"], "Yoga can help with flexibility, stress reduction, and body awareness. It works well as part of a broader PCOD routine."),
    ("exercise_pcod_home", "Home workout for PCOD", "exercise_pcod", ["pcod", "home workout", "exercise at home"], "At home, you can try walking in place, squats, glute bridges, wall push-ups, and stretching. Keep sessions simple so they are easier to repeat."),
    ("exercise_pcod_cycle", "Exercise consistency in PCOD", "exercise_pcod", ["pcod", "consistent", "routine", "habit"], "With PCOD, regular movement is usually more useful than intense workouts done rarely. Small consistent routines are powerful."),
    ("exercise_pcod_weight", "Exercise and weight management in PCOD", "exercise_pcod", ["pcod", "weight", "exercise", "loss"], "Exercise supports weight management best when paired with regular meals, enough sleep, and realistic goals. Focus on habits, not punishment."),
    ("exercise_pcod_overtraining", "Avoiding overtraining in PCOD", "exercise_pcod", ["pcod", "overtraining", "too much exercise"], "Very intense routines without enough rest can feel hard to maintain. A balanced routine with rest days is usually more sustainable."),
    ("exercise_pcod_schedule", "Weekly exercise plan for PCOD", "exercise_pcod", ["pcod", "weekly plan", "schedule"], "A simple weekly plan can be walking most days, strength training two or three days, and stretching or yoga once or twice."),
    ("exercise_pcod_morning", "Morning movement for PCOD", "exercise_pcod", ["pcod", "morning exercise", "start day"], "Morning movement can make the day feel structured and may improve consistency. Even a short walk counts."),
    ("exercise_pcod_evening", "Evening movement for PCOD", "exercise_pcod", ["pcod", "evening walk", "night exercise"], "An evening walk or light workout can still be helpful. The best time to exercise is the time you can do regularly."),
    ("exercise_pcod_low_energy", "Exercising when energy is low", "exercise_pcod", ["pcod", "low energy", "tired", "exercise"], "If energy is low, choose gentle movement like walking, stretching, or short beginner workouts. Starting small is still progress."),
    ("exercise_pcod_realistic", "Realistic workout advice for PCOD", "exercise_pcod", ["pcod", "realistic", "workout", "easy start"], "You do not need a perfect workout plan. A repeatable routine with walking, strength work, and rest is often enough to make a difference."),
    ("exercise_pcod_reassurance", "Exercise reassurance for PCOD", "exercise_pcod", ["pcod", "exercise", "worried", "beginner"], "You do not need to exercise for hours to support PCOD. Regular, moderate movement is a strong place to begin.")
]

exercise_stress_items = [
    ("exercise_stress_basics", "Exercise basics for stress relief", "exercise_stress", ["stress", "exercise", "relief", "movement"], "For stress relief, gentle movement is often a good place to start. Walking, stretching, and beginner yoga can help release tension."),
    ("exercise_stress_breathing", "Breathing exercises for stress", "exercise_stress", ["stress", "breathing", "calm", "panic"], "Breathing exercises can help slow the body down when stress is high. Keep it gentle and steady instead of forcing big breaths."),
    ("exercise_stress_walking", "Walking for stress relief", "exercise_stress", ["stress", "walking", "outside", "calm"], "Walking is a simple way to reduce stress. Fresh air, sunlight, and movement can all help your body feel less tense."),
    ("exercise_stress_stretching", "Stretching for stress", "exercise_stress", ["stress", "stretching", "neck", "shoulders"], "Stress often shows up as tight shoulders, jaw, and neck muscles. Gentle stretching can help your body loosen up."),
    ("exercise_stress_yoga", "Yoga for stress", "exercise_stress", ["stress", "yoga", "relax", "mind"], "Yoga can help with breathing, posture, and calming the nervous system. A beginner routine is enough to start."),
    ("exercise_stress_short", "Short exercise when stressed", "exercise_stress", ["stress", "short workout", "5 minutes", "quick"], "Even five to ten minutes of movement can help when stress is high. Try walking, stretching, or light body movement."),
    ("exercise_stress_evening", "Evening movement for stress", "exercise_stress", ["stress", "evening", "night", "walk"], "A light evening walk or stretch can help you unwind and reduce built-up tension from the day."),
    ("exercise_stress_morning", "Morning movement for stress", "exercise_stress", ["stress", "morning", "start day", "exercise"], "Starting the day with light movement can help you feel less stuck and more focused. It does not need to be long."),
    ("exercise_stress_anxiety", "Movement when anxious", "exercise_stress", ["stress", "anxiety", "restless", "movement"], "When you feel anxious, gentle movement can be easier than sitting still with racing thoughts. Try slow walking or stretching first."),
    ("exercise_stress_low_energy", "Exercise when tired and stressed", "exercise_stress", ["stress", "tired", "low energy", "exercise"], "If you are tired and stressed, choose the smallest version of movement that feels possible, such as stretching for a few minutes or a short walk."),
    ("exercise_stress_routine", "Stress relief routine with movement", "exercise_stress", ["stress", "routine", "exercise plan"], "A simple stress-relief movement routine can be walking most days, stretching, and a few minutes of slow breathing."),
    ("exercise_stress_body", "Why movement helps stress", "exercise_stress", ["stress", "body", "tension", "exercise"], "Movement can lower muscle tension, improve sleep, and make stress feel less trapped in the body."),
    ("exercise_stress_no_gym", "Stress relief without gym", "exercise_stress", ["stress", "no gym", "home movement", "easy"], "You do not need a gym for stress relief. Walking, stretching, yoga videos, and bodyweight exercises at home can help."),
    ("exercise_stress_realistic", "Realistic exercise advice for stress", "exercise_stress", ["stress", "realistic", "exercise", "small steps"], "When stress is high, the best exercise is the one you can actually do. Small regular sessions are enough to begin."),
    ("exercise_stress_reassurance", "Exercise reassurance for stress", "exercise_stress", ["stress", "exercise", "reassurance", "beginner"], "You do not need intense workouts to feel better. Gentle movement is valid and often easier to sustain.")
]

combined_items = [
    ("combined_pcod_stress_basics", "When PCOD and stress happen together", "combined", ["pcod", "stress", "together", "routine"], "When PCOD and stress happen together, focus on a repeatable routine: regular meals, protein at breakfast, daily walking, enough sleep, and one stress tool like journaling or breathing."),
    ("combined_start_small", "Start small when both PCOD and stress feel heavy", "combined", ["pcod", "stress", "small steps", "beginner"], "If both PCOD and stress feel heavy, begin with very small actions: drink water, eat one balanced meal, walk for ten minutes, and aim for a consistent bedtime."),
    ("combined_sleep_priority", "Why sleep matters when both are present", "combined", ["pcod", "stress", "sleep", "routine"], "Sleep supports both stress recovery and hormone-related routines. A steady bedtime can help everything else feel easier."),
    ("combined_breakfast", "Breakfast when managing PCOD and stress", "combined", ["pcod", "stress", "breakfast", "morning"], "A breakfast with protein and fiber, like eggs, oats, curd, or paneer, can support steadier energy and help avoid feeling drained early in the day."),
    ("combined_movement", "Movement when dealing with PCOD and stress", "combined", ["pcod", "stress", "exercise", "walking"], "Gentle regular movement is usually better than pushing too hard. Walking, yoga, and light strength work can support both stress and PCOD routines."),
    ("combined_cravings", "Managing cravings with PCOD and stress", "combined", ["pcod", "stress", "cravings", "snacks"], "Cravings can feel stronger when you are stressed, tired, or skipping meals. Balanced meals and planned snacks may help make things steadier."),
    ("combined_evening", "Evening routine for PCOD and stress", "combined", ["pcod", "stress", "evening", "sleep"], "A simple evening routine can include lighter screens, stretching, dinner on time, and a fixed sleep window. This can support both stress and hormonal routines."),
    ("combined_morning", "Morning routine for PCOD and stress", "combined", ["pcod", "stress", "morning", "reset"], "A gentle morning routine can include sunlight, water, breakfast, and a short walk. Starting calmly often makes the day easier."),
    ("combined_energy", "Low energy with PCOD and stress", "combined", ["pcod", "stress", "low energy", "tired"], "Low energy is common when stress and hormone-related issues overlap. Regular meals, movement, hydration, and sleep are often the basics to revisit."),
    ("combined_weight", "Weight concerns with PCOD and stress", "combined", ["pcod", "stress", "weight", "routine"], "Stress can make weight management harder by affecting sleep, cravings, and routine. Kind, steady habits usually work better than harsh plans."),
    ("combined_hormones", "Hormone-friendly habits under stress", "combined", ["pcod", "stress", "hormones", "habits"], "Hormone-friendly habits under stress include simple meals, steady sleep, reduced all-or-nothing thinking, and movement that feels doable."),
    ("combined_selfcare", "Self-care for PCOD and stress", "combined", ["pcod", "stress", "self care", "support"], "Self-care can be practical: meals on time, enough water, movement, rest, and speaking kindly to yourself while building new habits."),
    ("combined_doctor", "When to seek help for both PCOD and stress", "combined", ["pcod", "stress", "doctor", "counselor"], "Consider extra support if symptoms are affecting sleep, mood, daily function, or your periods. A doctor or counselor can help you make a better plan."),
    ("combined_reassurance", "Reassurance when both feel difficult", "combined", ["pcod", "stress", "worried", "hard"], "It is understandable to feel frustrated when stress and PCOD affect each other. Improvement usually comes from small repeatable habits rather than perfect days."),
    ("combined_day_plan", "Simple day plan for PCOD and stress", "combined", ["pcod", "stress", "day plan", "routine"], "A simple day plan can include breakfast with protein, one or two balanced meals, water, a walk, a short breathing break, and sleep on time.")
]

for item in pcod_items + stress_items + diet_pcod_items + diet_stress_items + exercise_pcod_items + exercise_stress_items + combined_items:
    add(*item)

if len(entries) != 100:
    raise ValueError(f"Expected 100 entries, got {len(entries)}")

os.makedirs(DATA_DIR, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print("Created:", OUTPUT_PATH)
print("Total entries:", len(entries))