
// Workout plan data structure
export const workoutPlan = {
    weeklySchedule: [
      { day: "Monday", morning: "Sprint Intervals + Abs", evening: "Upper Body Strength (Push focus)" },
      { day: "Tuesday", morning: "Abs + Fast Walk/Light Jog", evening: "Lower Body Strength (Glutes focus)" },
      { day: "Wednesday", morning: "Abs + Fast Walk", evening: "Upper Body (Pull focus)" },
      { day: "Thursday", morning: "Abs + Fast Walk", evening: "Lower Body (Hamstrings & Quads)" },
      { day: "Friday", morning: "Abs + Light Cardio", evening: "Full Body Functional/HIIT" },
      { day: "Saturday", morning: "Long Outdoor Run + Abs", evening: "Light Weights or Active Recovery" },
      { day: "Sunday", morning: "Abs + Stretching", evening: "Skipping Rope (HIIT) – 45 min" }
    ],
    abWorkout: [
      { exercise: "Plank", setsReps: "3 x 45 sec" },
      { exercise: "Russian Twists", setsReps: "3 x 30 reps (15/side)" },
      { exercise: "Leg Raises", setsReps: "3 x 15 reps" },
      { exercise: "Bicycle Crunches", setsReps: "3 x 20 reps (10/side)" },
      { exercise: "Mountain Climbers", setsReps: "3 x 30 sec" },
      { exercise: "Flutter Kicks", setsReps: "3 x 30 sec" }
    ],
    weightTraining: {
      Monday: {
        title: "Push - Chest, Shoulders, Triceps",
        exercises: [
          { exercise: "Barbell Bench Press", setsReps: "4 x 10" },
          { exercise: "Shoulder Press (Dumbbell)", setsReps: "3 x 12" },
          { exercise: "Incline Dumbbell Press", setsReps: "3 x 10" },
          { exercise: "Dumbbell Lateral Raises", setsReps: "3 x 15" },
          { exercise: "Tricep Dips", setsReps: "3 x 15" },
          { exercise: "Push-Ups (Finisher)", setsReps: "2 x Max" }
        ]
      },
      Tuesday: {
        title: "Glutes & Legs (Posterior Chain)",
        exercises: [
          { exercise: "Barbell Hip Thrusts", setsReps: "4 x 12" },
          { exercise: "Romanian Deadlifts", setsReps: "4 x 10" },
          { exercise: "Cable Kickbacks", setsReps: "3 x 15" },
          { exercise: "Walking Lunges", setsReps: "3 x 12 per leg" },
          { exercise: "Glute Bridges", setsReps: "3 x 20" }
        ]
      },
      Wednesday: {
        title: "Pull - Back & Biceps",
        exercises: [
          { exercise: "Lat Pulldown or Pullups", setsReps: "3 x 10" },
          { exercise: "Dumbbell Rows", setsReps: "4 x 10 per side" },
          { exercise: "Seated Cable Rows", setsReps: "3 x 12" },
          { exercise: "Barbell Curls", setsReps: "3 x 12" },
          { exercise: "Hammer Curls", setsReps: "3 x 12" }
        ]
      },
      Thursday: {
        title: "Legs - Quads, Hamstrings",
        exercises: [
          { exercise: "Barbell Squats", setsReps: "4 x 10" },
          { exercise: "Leg Press", setsReps: "3 x 12" },
          { exercise: "Bulgarian Split Squats", setsReps: "3 x 10 per leg" },
          { exercise: "Hamstring Curls", setsReps: "3 x 15" },
          { exercise: "Calf Raises", setsReps: "3 x 20" }
        ]
      },
      Friday: {
        title: "Full Body Functional/HIIT",
        exercises: [
          { exercise: "Kettlebell Swings", setsReps: "4 x 15" },
          { exercise: "Box Jumps or Jump Squats", setsReps: "3 x 15" },
          { exercise: "Dumbbell Thrusters", setsReps: "3 x 12" },
          { exercise: "Renegade Rows", setsReps: "3 x 12" },
          { exercise: "Burpees", setsReps: "3 x 15" }
        ]
      },
      Saturday: {
        title: "Active Recovery (Light Weights + Mobility)",
        exercises: [
          { exercise: "Light Dumbbell Curls", setsReps: "2 x 15" },
          { exercise: "Lateral Band Walks", setsReps: "2 x 20 steps" },
          { exercise: "Stability Ball Crunches", setsReps: "2 x 15" },
          { exercise: "Resistance Band Rows", setsReps: "2 x 15" },
          { exercise: "Deep Stretch/Yoga Flow", setsReps: "15 min" }
        ]
      },
      Sunday: {
        title: "Cardio – Skipping Rope Routine",
        exercises: [
          { exercise: "Skipping Intervals", setsReps: "5 min warmup + 10 rounds 2-min skip / 1-min rest" },
          { exercise: "Jump Variations", setsReps: "Alternate feet, high knees" },
          { exercise: "Cooldown Stretch", setsReps: "10 min total body" }
        ]
      }
    }
  };
  
  // Motivational quotes array
  export const motivationalQuotes = [
    "It's not about being the best. It's about being better than you were yesterday.",
    "The only bad workout is the one that didn't happen.",
    "Your body can stand almost anything. It's your mind that you have to convince.",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Don't wish for it. Work for it.",
    "Nothing worth having comes easy.",
    "The hard days are what make you stronger.",
    "You don't have to be extreme, just consistent.",
    "Discipline is choosing between what you want now and what you want most.",
    "Remember why you started."
  ];