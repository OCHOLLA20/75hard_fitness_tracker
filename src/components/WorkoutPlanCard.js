import React from 'react';

/**
 * WorkoutPlanCard component displays workout information in a styled card format
 * 
 * @param {string} title - The title of the workout (e.g., "Morning Workout")
 * @param {string} description - The workout description
 * @param {string} time - Optional timing information (e.g., "Complete before noon")
 * @returns {JSX.Element} - Rendered component
 */
const WorkoutPlanCard = ({ title, description, time }) => {
  return (
    <div className="p-4 bg-sky-50 border-l-4 border-sky-500 rounded-lg mb-3">
      <h4 className="font-bold text-sky-600">{title}</h4>
      <p className="text-sm text-slate-600">{description}</p>
      {time && <p className="text-xs text-slate-500 mt-1">{time}</p>}
    </div>
  );
};

export default WorkoutPlanCard;