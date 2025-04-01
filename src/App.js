import React, { useState, useEffect, useMemo } from 'react';
import { 
  Calendar, Droplet, Menu, X, BarChart2, Home,
  Droplets, Dumbbell, PlusCircle, Trash2, User, Plus, Bell
} from 'lucide-react';
import useLocalStorage from './hooks/useLocalStorage';
import './App.css';
import './index.css';
import TaskCard from './components/TaskCard';
import WorkoutPlanCard from './components/WorkoutPlanCard';
import { workoutPlan, motivationalQuotes } from './data/workoutData';

const HardTracker = () => {
  // Get current date information
  const today = new Date();
  const currentDay = today.getDay(); // 0 is Sunday, 1 is Monday, etc.
  const weekdays = useMemo(() => ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], []);
  const currentWeekday = weekdays[currentDay];
  
  // State management
  const [currentDayNumber, setCurrentDayNumber] = useLocalStorage('currentDayNumber', 1);
  const [completedDays, setCompletedDays] = useLocalStorage('completedDays', []);
  const [tasks, setTasks] = useLocalStorage('todayTasks', {
    morningWorkout: false,
    eveningWorkout: false,
    diet: false,
    water1: false,
    water2: false,
    water3: false,
    water4: false,
    progressPhoto: false,
    reading: false
  });
  
  // Navigation state
  const [activeTab, setActiveTab] = useState('home');
  const [menuOpen, setMenuOpen] = useState(false);
  
  // Workout tracking state
  const [workouts, setWorkouts] = useLocalStorage('workouts', {});
  const [currentExercise, setCurrentExercise] = useState({
    name: '',
    weight: '',
    sets: '',
    reps: '',
    notes: ''
  });
  const [selectedDay, setSelectedDay] = useState(currentDayNumber);
  const [selectedWeekday, setSelectedWeekday] = useState(currentWeekday);
  
  // Workouts tab view state
  const [workoutView, setWorkoutView] = useState('plan'); // 'plan' or 'logs'
  
  // Random quote for motivation
  const [quote, setQuote] = useState('');
  
  useEffect(() => {
    // Set a random motivational quote
    const randomIndex = Math.floor(Math.random() * motivationalQuotes.length);
    setQuote(motivationalQuotes[randomIndex]);
  }, []);
  
  // Calculate progress
  const progressPercentage = Math.floor((completedDays.length / 75) * 100);
  const tasksCompletedCount = Object.values(tasks).filter(Boolean).length;
  const tasksCompletedPercentage = Math.floor((tasksCompletedCount / 9) * 100);

  // Update selected weekday when selectedDay changes
  useEffect(() => {
    // Calculate the weekday for the selected day
    // This is a simplified approach - adjusts based on current weekday and day number
    const dayDifference = selectedDay - currentDayNumber;
    const newWeekdayIndex = (currentDay + dayDifference) % 7;
    const adjustedIndex = newWeekdayIndex < 0 ? 7 + newWeekdayIndex : newWeekdayIndex;
    setSelectedWeekday(weekdays[adjustedIndex]);
  }, [selectedDay, currentDayNumber, currentDay, weekdays]);

  // Handle task toggling
  const toggleTask = (taskName) => {
    setTasks({
      ...tasks,
      [taskName]: !tasks[taskName]
    });
  };
  
  // Complete the current day
  const completeDay = () => {
    if (!completedDays.includes(currentDayNumber)) {
      setCompletedDays([...completedDays, currentDayNumber]);
      setCurrentDayNumber(currentDayNumber + 1);
    }
  };
  
  // Workout tracking functions
  const handleExerciseChange = (e) => {
    const { name, value } = e.target;
    setCurrentExercise({
      ...currentExercise,
      [name]: value
    });
  };
  
  const addExercise = () => {
    if (!currentExercise.name) return;
    
    const dayKey = `day-${selectedDay}`;
    const currentDayWorkouts = workouts[dayKey] || [];
    
    setWorkouts({
      ...workouts,
      [dayKey]: [...currentDayWorkouts, { 
        ...currentExercise, 
        id: Date.now().toString()
      }]
    });
    
    // Reset form
    setCurrentExercise({
      name: '',
      weight: '',
      sets: '',
      reps: '',
      notes: ''
    });
  };
  
  const deleteExercise = (dayKey, exerciseId) => {
    const currentDayWorkouts = workouts[dayKey] || [];
    const updatedWorkouts = currentDayWorkouts.filter(ex => ex.id !== exerciseId);
    
    setWorkouts({
      ...workouts,
      [dayKey]: updatedWorkouts
    });
  };
  
  // Prefill an exercise from the template
  const prefillExercise = (exercise, setsReps) => {
    // Parse sets and reps from the setsReps string
    let sets = '';
    let reps = '';
    
    if (setsReps) {
      const match = setsReps.match(/(\d+)\s*x\s*(\d+|Max|max|\d+\s*sec|\d+\s*min)/);
      if (match) {
        sets = match[1];
        reps = match[2];
      }
    }
    
    setCurrentExercise({
      name: exercise,
      weight: '',
      sets: sets,
      reps: reps,
      notes: ''
    });
  };
  
  // Add all exercises from a workout template to the daily tracking
  const addAllFromTemplate = (exercises) => {
    if (!exercises || exercises.length === 0) return;
    
    const dayKey = `day-${selectedDay}`;
    const currentDayWorkouts = workouts[dayKey] || [];
    
    const newExercises = exercises.map(ex => ({
      name: ex.exercise,
      sets: ex.setsReps.split('x')[0]?.trim() || '',
      reps: ex.setsReps.split('x')[1]?.trim() || '',
      weight: '',
      notes: '',
      id: `template-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }));
    
    setWorkouts({
      ...workouts,
      [dayKey]: [...currentDayWorkouts, ...newExercises]
    });
  };
  
  // Map the current day to the appropriate schedule
  const getCurrentWorkoutSchedule = () => {
    return workoutPlan.weeklySchedule.find(schedule => schedule.day === currentWeekday) || {
      morning: "Rest Day", 
      evening: "Rest Day"
    };
  };
  
  // Get the workout template for the selected weekday
  const getSelectedDayWorkout = () => {
    return workoutPlan.weightTraining[selectedWeekday] || null;
  };
  
  // Render the calendar grid
  const renderCalendarGrid = () => {
    const days = [];
    for (let i = 1; i <= 75; i++) {
      const isCompleted = completedDays.includes(i);
      const isCurrent = i === currentDayNumber;
      
      days.push(
        <div 
          key={i} 
          className={`flex items-center justify-center w-10 h-10 rounded-full 
            ${isCompleted ? 'bg-lime-500 text-white' : 'bg-gray-100'} 
            ${isCurrent ? 'ring-2 ring-sky-400 font-bold' : ''}`}
        >
          {i}
        </div>
      );
    }
    return days;
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header - Using sky blue instead of red */}
      <header className="bg-sky-600 text-white shadow-md sticky top-0 z-20">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center">
            <button 
              className="mr-3 md:hidden" 
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <Menu size={24} />
            </button>
            <h1 className="text-2xl font-bold tracking-wide">75 Hard Tracker</h1>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2">
              <Bell size={20} />
            </button>
            <div className="bg-sky-700 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
              <span>Day {currentDayNumber}/75</span>
              <span role="img" aria-label="sun">🌞</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1">
        {/* Side Navigation - Hidden on mobile, using sky blue instead of gray-800 */}
        <aside className={`bg-zinc-800 text-white w-64 fixed h-full z-30 transform transition-transform duration-300 ease-in-out md:translate-x-0 ${menuOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:block`}>
          <div className="flex justify-between items-center p-4 border-b border-zinc-700">
            <h2 className="font-bold text-xl">Menu</h2>
            <button className="md:hidden" onClick={() => setMenuOpen(false)}>
              <X size={20} />
            </button>
          </div>
          <nav className="p-4">
            <ul className="space-y-2">
              <li>
                <button 
                  onClick={() => { setActiveTab('home'); setMenuOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${activeTab === 'home' ? 'bg-sky-600' : 'hover:bg-zinc-700'}`}
                >
                  <Home size={20} />
                  <span>Dashboard</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => { setActiveTab('calendar'); setMenuOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${activeTab === 'calendar' ? 'bg-sky-600' : 'hover:bg-zinc-700'}`}
                >
                  <Calendar size={20} />
                  <span>Calendar</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => { setActiveTab('workouts'); setMenuOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${activeTab === 'workouts' ? 'bg-sky-600' : 'hover:bg-zinc-700'}`}
                >
                  <Dumbbell size={20} />
                  <span>Workouts</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => { setActiveTab('stats'); setMenuOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${activeTab === 'stats' ? 'bg-sky-600' : 'hover:bg-zinc-700'}`}
                >
                  <BarChart2 size={20} />
                  <span>Statistics</span>
                </button>
              </li>
              <li>
                <button 
                  onClick={() => { setActiveTab('profile'); setMenuOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${activeTab === 'profile' ? 'bg-sky-600' : 'hover:bg-zinc-700'}`}
                >
                  <User size={20} />
                  <span>Profile</span>
                </button>
              </li>
            </ul>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 px-4 py-6 md:px-8 pb-20 md:pb-6">
          {activeTab === 'home' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              {/* Header with motivation */}
              <div className="bg-gradient-to-r from-sky-50 to-sky-100 rounded-xl shadow-sm p-6 border border-sky-200">
                <h2 className="text-xl font-bold text-zinc-800">Day {currentDayNumber} 🔥 Keep Going!</h2>
                <p className="text-slate-600 mt-2 italic">"{quote}"</p>
              </div>
              
              {/* Swipeable Task Cards */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Today's Tasks</h2>
                <div className="overflow-x-auto pb-2">
                  <div className="flex space-x-2 md:space-x-4 py-2">
                    <TaskCard 
                      icon="🌞" 
                      title="Morning Workout" 
                      isCompleted={tasks.morningWorkout}
                      onClick={() => toggleTask('morningWorkout')}
                    />
                    <TaskCard 
                      icon="🌙" 
                      title="Evening Workout" 
                      isCompleted={tasks.eveningWorkout}
                      onClick={() => toggleTask('eveningWorkout')}
                    />
                    <TaskCard 
                      icon="🍽️" 
                      title="OMAD Diet" 
                      isCompleted={tasks.diet}
                      onClick={() => toggleTask('diet')}
                    />
                    <TaskCard 
                      icon="📚" 
                      title="Read 10 Pages" 
                      isCompleted={tasks.reading}
                      onClick={() => toggleTask('reading')}
                    />
                    <TaskCard 
                      icon="📸" 
                      title="Progress Photo" 
                      isCompleted={tasks.progressPhoto}
                      onClick={() => toggleTask('progressPhoto')}
                    />
                  </div>
                </div>
              </div>
              
              {/* Progress Overview */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Challenge Progress</h2>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-slate-600">Overall: {progressPercentage}% complete</span>
                  <span className="text-sm font-medium">{completedDays.length}/75 days</span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full"
                    style={{ width: `${progressPercentage}%` }}
                  ></div>
                </div>
                
                <div className="flex justify-between items-center mt-4 mb-2">
                  <span className="text-sm text-slate-600">Today: {tasksCompletedPercentage}% complete</span>
                  <span className="text-sm font-medium">{tasksCompletedCount}/9 tasks</span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-sky-400 to-sky-500 rounded-full"
                    style={{ width: `${tasksCompletedPercentage}%` }}
                  ></div>
                </div>

                {/* Complete Day button */}
                <div className="mt-4">
                  <button 
                    onClick={completeDay}
                    className="bg-lime-500 text-white px-4 py-2 rounded-lg hover:bg-lime-600 transition-colors"
                    disabled={tasksCompletedCount < 9}
                  >
                    Complete Day {currentDayNumber}
                  </button>
                  {tasksCompletedCount < 9 && (
                    <p className="text-sm text-amber-500 mt-2">Complete all tasks before marking the day as complete</p>
                  )}
                </div>
              </div>
              
              {/* Water Tracker with rounded buttons */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Water Intake</h2>
                <p className="text-slate-600 mb-4">1 gallon (≈ 4 liters) daily</p>
                
                <div className="flex justify-between items-center gap-2">
                  <div className="flex-1">
                    <button 
                      onClick={() => toggleTask('water1')}
                      className={`w-full h-16 rounded-lg flex items-center justify-center transition-colors ${tasks.water1 ? 'bg-sky-500 text-white' : 'bg-sky-100 text-sky-800'}`}
                    >
                      <Droplet size={28} />
                    </button>
                    <p className="text-center text-xs mt-1 text-slate-500">1L</p>
                  </div>
                  
                  <div className="flex-1">
                    <button 
                      onClick={() => toggleTask('water2')}
                      className={`w-full h-16 rounded-lg flex items-center justify-center transition-colors ${tasks.water2 ? 'bg-sky-500 text-white' : 'bg-sky-100 text-sky-800'}`}
                    >
                      <Droplet size={28} />
                    </button>
                    <p className="text-center text-xs mt-1 text-slate-500">2L</p>
                  </div>
                  
                  <div className="flex-1">
                    <button 
                      onClick={() => toggleTask('water3')}
                      className={`w-full h-16 rounded-lg flex items-center justify-center transition-colors ${tasks.water3 ? 'bg-sky-500 text-white' : 'bg-sky-100 text-sky-800'}`}
                    >
                      <Droplet size={28} />
                    </button>
                    <p className="text-center text-xs mt-1 text-slate-500">3L</p>
                  </div>
                  
                  <div className="flex-1">
                    <button 
                      onClick={() => toggleTask('water4')}
                      className={`w-full h-16 rounded-lg flex items-center justify-center transition-colors ${tasks.water4 ? 'bg-sky-500 text-white' : 'bg-sky-100 text-sky-800'}`}
                    >
                      <Droplets size={28} />
                    </button>
                    <p className="text-center text-xs mt-1 text-slate-500">4L</p>
                  </div>
                </div>
              </div>
              
              {/* Today's Workout Plan */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Today's Workout Plan</h2>
                <div className="space-y-4">
                  <WorkoutPlanCard 
                    title="Morning Workout" 
                    description={getCurrentWorkoutSchedule().morning}
                    time="Complete before noon"
                  />
                  <WorkoutPlanCard 
                    title="Evening Workout" 
                    description={getCurrentWorkoutSchedule().evening}
                    time="Complete after 5 PM"
                  />
                </div>
                <div className="mt-4">
                  <button 
                    onClick={() => setActiveTab('workouts')}
                    className="bg-sky-500 text-white px-4 py-2 rounded-lg hover:bg-sky-600 transition-colors"
                  >
                    View Full Workout Details
                  </button>
                </div>
              </div>
              
              {/* Notes */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Today's Notes</h2>
                <textarea 
                  className="w-full border border-gray-300 rounded-lg p-3 min-h-32 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                  placeholder="Add workout notes, feelings, or achievements..."
                ></textarea>
              </div>
            </div>
          )}
          
          {activeTab === 'calendar' && (
            <div className="bg-white rounded-xl shadow-sm p-6 max-w-4xl mx-auto">
              <h2 className="text-xl font-bold mb-6 text-zinc-800">75 Day Progress Calendar</h2>
              <div className="grid grid-cols-5 sm:grid-cols-7 md:grid-cols-10 lg:grid-cols-15 gap-3 md:gap-4">
                {renderCalendarGrid()}
              </div>
              
              {/* Calendar day details */}
              <div className="mt-8 p-4 border-t border-gray-200">
                <h3 className="font-bold text-lg text-zinc-800 mb-4">Selected Day Details</h3>
                <p className="text-slate-600">Click on a day in the calendar to view detailed information for that day.</p>
              </div>
            </div>
          )}
          
          {activeTab === 'workouts' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              {/* Workout view tabs */}
              <div className="flex border-b border-gray-200">
                <button 
                  onClick={() => setWorkoutView('plan')}
                  className={`py-3 px-4 font-medium ${workoutView === 'plan' ? 'text-sky-600 border-b-2 border-sky-500' : 'text-slate-600 hover:text-sky-500'}`}
                >
                  Today's Plan
                </button>
                <button 
                  onClick={() => setWorkoutView('logs')}
                  className={`py-3 px-4 font-medium ${workoutView === 'logs' ? 'text-sky-600 border-b-2 border-sky-500' : 'text-slate-600 hover:text-sky-500'}`}
                >
                  My Logs
                </button>
              </div>
              
              {workoutView === 'plan' ? (
                <>
                  {/* Today's Workout Plan */}
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="text-xl font-bold mb-4 text-zinc-800">Workout Plan for {currentWeekday}</h2>
                    <div className="space-y-4">
                      <WorkoutPlanCard 
                        title="Morning Workout" 
                        description={getCurrentWorkoutSchedule().morning}
                      />
                      <WorkoutPlanCard 
                        title="Evening Workout" 
                        description={getCurrentWorkoutSchedule().evening}
                      />
                    </div>
                  </div>
                  
                  {/* Daily Ab Workout Section */}
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="text-xl font-bold mb-4 text-zinc-800">Daily Ab Workout (10-15 minutes)</h2>
                    <p className="text-slate-600 mb-4">Complete after morning cardio or before evening session</p>
                    
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse">
                        <thead>
                          <tr className="bg-gray-100">
                            <th className="text-left p-3 text-zinc-700">Exercise</th>
                            <th className="text-center p-3 text-zinc-700">Sets x Reps</th>
                            <th className="text-center p-3 text-zinc-700">Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {workoutPlan.abWorkout.map((exercise, index) => (
                            <tr key={index} className="border-b border-gray-200">
                              <td className="p-3 font-medium">{exercise.exercise}</td>
                              <td className="p-3 text-center">{exercise.setsReps}</td>
                              <td className="p-3 text-center">
                                <button 
                                  onClick={() => prefillExercise(exercise.exercise, exercise.setsReps)}
                                  className="text-sky-500 hover:text-sky-700 p-1"
                                >
                                  <PlusCircle size={18} />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    
                    <p className="text-sm text-slate-500 mt-4">Optional: Add weighted crunches twice a week (3 x 15)</p>
                  </div>
                  
                  {/* Daily Workout Templates */}
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="text-xl font-bold mb-4 text-zinc-800">{currentWeekday} Strength Training</h2>
                    
                    {getSelectedDayWorkout() ? (
                      <div>
                        <div className="mb-4 p-3 bg-gradient-to-r from-sky-50 to-sky-100 rounded-lg">
                          <h3 className="font-bold text-lg text-zinc-800">{getSelectedDayWorkout().title}</h3>
                        </div>
                        
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse">
                            <thead>
                              <tr className="bg-gray-100">
                                <th className="text-left p-3 text-zinc-700">Exercise</th>
                                <th className="text-center p-3 text-zinc-700">Sets x Reps</th>
                                <th className="text-center p-3 text-zinc-700">Action</th>
                              </tr>
                            </thead>
                            <tbody>
                              {getSelectedDayWorkout().exercises.map((exercise, index) => (
                                <tr key={index} className="border-b border-gray-200">
                                  <td className="p-3 font-medium">{exercise.exercise}</td>
                                  <td className="p-3 text-center">{exercise.setsReps}</td>
                                  <td className="p-3 text-center">
                                    <button 
                                      onClick={() => prefillExercise(exercise.exercise, exercise.setsReps)}
                                      className="text-sky-500 hover:text-sky-700 p-1"
                                    >
                                      <PlusCircle size={18} />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        <div className="mt-4 flex justify-end">
                          <button 
                            onClick={() => {
                              addAllFromTemplate(getSelectedDayWorkout().exercises);
                              setWorkoutView('logs');
                            }}
                            className="bg-lime-500 text-white px-4 py-2 rounded-lg hover:bg-lime-600 transition-colors flex items-center gap-2"
                          >
                            <Dumbbell size={18} />
                            Add All to Tracking
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-slate-500">
                        <p>No workout template available for {currentWeekday}</p>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  {/* Workout Tracker Section */}
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <div className="flex flex-wrap justify-between items-center mb-6">
                      <h2 className="text-xl font-bold text-zinc-800">Workout Tracker</h2>
                      <div className="flex items-center gap-2 mt-2 sm:mt-0">
                        <label htmlFor="daySelect" className="text-zinc-700">Day:</label>
                        <select 
                          id="daySelect" 
                          className="border border-gray-300 rounded-lg p-2"
                          value={selectedDay}
                          onChange={(e) => setSelectedDay(parseInt(e.target.value))}
                        >
                          {[...Array(75)].map((_, i) => (
                            <option key={i+1} value={i+1}>Day {i+1} ({weekdays[(currentDay + (i+1) - currentDayNumber) % 7]})</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Add Exercise Form */}
                    <div className="mb-8">
                      <h3 className="font-medium text-zinc-800 mb-4">Add Exercise</h3>
                      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <div className="md:col-span-2">
                          <label htmlFor="exerciseName" className="block text-sm text-slate-600 mb-1">Exercise Name</label>
                          <input 
                            id="exerciseName"
                            name="name"
                            value={currentExercise.name}
                            onChange={handleExerciseChange}
                            type="text" 
                            placeholder="Bench Press, Squat, etc."
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                          />
                        </div>
                        <div>
                          <label htmlFor="weight" className="block text-sm text-slate-600 mb-1">Weight (lbs)</label>
                          <input 
                            id="weight"
                            name="weight"
                            value={currentExercise.weight}
                            onChange={handleExerciseChange}
                            type="number" 
                            placeholder="135"
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                          />
                        </div>
                        <div>
                          <label htmlFor="sets" className="block text-sm text-slate-600 mb-1">Sets</label>
                          <input 
                            id="sets"
                            name="sets"
                            value={currentExercise.sets}
                            onChange={handleExerciseChange}
                            type="number" 
                            placeholder="3"
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                          />
                        </div>
                        <div>
                          <label htmlFor="reps" className="block text-sm text-slate-600 mb-1">Reps</label>
                          <input 
                            id="reps"
                            name="reps"
                            value={currentExercise.reps}
                            onChange={handleExerciseChange}
                            type="text" 
                            placeholder="8-12"
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                          />
                        </div>
                      </div>
                      <div className="mt-4">
                        <label htmlFor="notes" className="block text-sm text-slate-600 mb-1">Notes</label>
                        <input 
                          id="notes"
                          name="notes"
                          value={currentExercise.notes}
                          onChange={handleExerciseChange}
                          type="text" 
                          placeholder="Optional: Form cues, difficulty level, etc."
                          className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                        />
                      </div>
                      <div className="mt-4 flex gap-2 justify-end">
                        <button 
                          onClick={addExercise}
                          className="bg-sky-500 text-white px-4 py-2 rounded-lg hover:bg-sky-600 transition-colors flex items-center gap-2"
                        >
                          <PlusCircle size={18} />
                          Add Exercise
                        </button>
                      </div>
                    </div>
                    
                    {/* Daily Tracked Exercises */}
                    <div>
                      <h3 className="font-medium text-zinc-800 mb-4">Day {selectedDay} Exercises</h3>
                      
                      {(!workouts[`day-${selectedDay}`] || workouts[`day-${selectedDay}`].length === 0) ? (
                        <div className="text-center py-8 text-slate-500">
                          <Dumbbell size={32} className="mx-auto mb-2 opacity-30" />
                          <p>No exercises logged for this day</p>
                          <p className="text-sm">Use the form above to add exercises</p>
                        </div>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse">
                            <thead>
                              <tr className="bg-gray-100">
                                <th className="text-left p-3 text-zinc-700">Exercise</th>
                                <th className="text-center p-3 text-zinc-700">Weight</th>
                                <th className="text-center p-3 text-zinc-700">Sets</th>
                                <th className="text-center p-3 text-zinc-700">Reps</th>
                                <th className="text-left p-3 text-zinc-700">Notes</th>
                                <th className="text-center p-3 text-zinc-700">Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              {workouts[`day-${selectedDay}`].map((exercise) => (
                                <tr key={exercise.id} className="border-b border-gray-200">
                                  <td className="p-3 font-medium">{exercise.name}</td>
                                  <td className="p-3 text-center">{exercise.weight}</td>
                                  <td className="p-3 text-center">{exercise.sets}</td>
                                  <td className="p-3 text-center">{exercise.reps}</td>
                                  <td className="p-3 text-sm text-slate-600">{exercise.notes}</td>
                                  <td className="p-3 text-center">
                                    <button 
                                      onClick={() => deleteExercise(`day-${selectedDay}`, exercise.id)}
                                      className="text-red-500 hover:text-red-700 p-1"
                                    >
                                      <Trash2 size={18} />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
          
          {activeTab === 'stats' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-6 text-zinc-800">Your Progress Stats</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-5 border border-amber-200">
                    <h3 className="text-sm font-medium text-amber-600 mb-1">Days Completed</h3>
                    <p className="text-3xl font-bold text-zinc-800">{completedDays.length} <span className="text-lg text-slate-500 font-normal">/ 75</span></p>
                  </div>
                  <div className="bg-gradient-to-br from-sky-50 to-sky-100 rounded-xl p-5 border border-sky-200">
                    <h3 className="text-sm font-medium text-sky-600 mb-1">Completion Rate</h3>
                    <p className="text-3xl font-bold text-zinc-800">{progressPercentage}%</p>
                  </div>
                  <div className="bg-gradient-to-br from-lime-50 to-lime-100 rounded-xl p-5 border border-lime-200">
                    <h3 className="text-sm font-medium text-lime-600 mb-1">Current Streak</h3>
                    <p className="text-3xl font-bold text-zinc-800">{completedDays.length} <span className="text-lg text-slate-500 font-normal">days</span></p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Weight Tracker</h2>
                <div className="flex gap-3 mb-4">
                  <input 
                    type="number" 
                    placeholder="Enter weight (lbs)"
                    className="flex-1 border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                  />
                  <button className="bg-sky-500 text-white px-4 py-2 rounded-lg hover:bg-sky-600 transition-colors">
                    Add
                  </button>
                </div>
                
                <div className="mt-6 text-center text-slate-500">
                  <p>No weight entries yet</p>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-4 text-zinc-800">Reading Progress</h2>
                <div className="bg-gradient-to-br from-sky-50 to-sky-100 rounded-lg p-4 border border-sky-200">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium text-sky-700">Current Book</h3>
                    <span className="text-sm bg-sky-200 text-sky-800 px-2 py-1 rounded-full">10 pages daily</span>
                  </div>
                  <p className="font-medium text-lg text-zinc-800">Self-Discipline Book</p>
                  <div className="mt-3">
                    <div className="flex justify-between text-sm text-slate-600 mb-1">
                      <span>Progress</span>
                      <span>0 / 250 pages</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-sky-500 rounded-full" style={{ width: '0%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* New Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex flex-col items-center md:flex-row md:items-start gap-6">
                  <div className="bg-sky-100 w-24 h-24 rounded-full flex items-center justify-center text-2xl font-bold text-sky-600">
                    UN
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-zinc-800 text-center md:text-left">75 Hard Challenger</h2>
                    <p className="text-slate-600 text-center md:text-left">Joined: April 1, 2025</p>
                    
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <h3 className="font-medium text-zinc-800">Challenge Start Date</h3>
                        <p className="text-slate-600">April 1, 2025</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <h3 className="font-medium text-zinc-800">Expected End Date</h3>
                        <p className="text-slate-600">June 15, 2025</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-bold mb-6 text-zinc-800">Settings</h2>
                
                <div className="space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6">
                    <label htmlFor="reminder" className="font-medium text-zinc-700 w-32">Daily Reminder:</label>
                    <select 
                      id="reminder" 
                      className="border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
                    >
                      <option value="6">6:00 AM</option>
                      <option value="7">7:00 AM</option>
                      <option value="8">8:00 AM</option>
                      <option value="9">9:00 AM</option>
                    </select>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="darkMode"
                      className="mr-2 h-4 w-4 text-sky-600"
                    />
                    <label htmlFor="darkMode" className="text-zinc-700">
                      Dark Mode
                    </label>
                  </div>
                  
                  <div className="pt-4 border-t border-gray-200">
                    <h3 className="font-medium text-zinc-800 mb-4">Export Data</h3>
                    <button className="bg-sky-100 text-sky-700 border border-sky-200 px-4 py-2 rounded-lg hover:bg-sky-200 transition-colors">
                      Export Progress Data
                    </button>
                  </div>
                  
                  <div className="pt-4 border-t border-gray-200">
                    <h3 className="font-medium text-zinc-800 mb-4">Reset Progress</h3>
                    <button className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                      Reset All Progress
                    </button>
                    <p className="mt-2 text-sm text-slate-500">This will reset all challenge progress. This action cannot be undone.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
      
      {/* Mobile Bottom Navigation with FAB */}
      <nav className="md:hidden bg-white border-t border-gray-200 fixed bottom-0 left-0 right-0 z-20">
        <div className="flex justify-around relative">
          <button 
            className={`flex-1 flex flex-col items-center justify-center py-2 ${activeTab === 'home' ? 'text-sky-600' : 'text-slate-600'}`}
            onClick={() => setActiveTab('home')}
          >
            <Home size={20} />
            <span className="text-xs mt-1">Home</span>
          </button>
          <button 
            className={`flex-1 flex flex-col items-center justify-center py-2 ${activeTab === 'calendar' ? 'text-sky-600' : 'text-slate-600'}`}
            onClick={() => setActiveTab('calendar')}
          >
            <Calendar size={20} />
            <span className="text-xs mt-1">Calendar</span>
          </button>
          
          {/* Floating Action Button */}
          <div className="absolute -top-6 inset-x-0 flex justify-center">
            <button className="w-12 h-12 bg-amber-500 text-white rounded-full shadow-lg flex items-center justify-center">
              <Plus size={24} />
            </button>
          </div>
          
          <button 
            className={`flex-1 flex flex-col items-center justify-center py-2 ${activeTab === 'workouts' ? 'text-sky-600' : 'text-slate-600'}`}
            onClick={() => setActiveTab('workouts')}
          >
            <Dumbbell size={20} />
            <span className="text-xs mt-1">Workouts</span>
          </button>
          <button 
            className={`flex-1 flex flex-col items-center justify-center py-2 ${activeTab === 'stats' ? 'text-sky-600' : 'text-slate-600'}`}
            onClick={() => setActiveTab('stats')}
          >
            <BarChart2 size={20} />
            <span className="text-xs mt-1">Stats</span>
          </button>
        </div>
      </nav>
    </div>
  );
};

export default HardTracker;