// TaskCard.js
import React from 'react';

const TaskCard = ({ icon, title, isCompleted, onClick }) => (
  <div 
    className="bg-white w-32 md:w-40 rounded-xl shadow-md p-4 text-center m-2 cursor-pointer transition-transform hover:scale-105"
    onClick={onClick}
  >
    <div className="text-3xl">{icon}</div>
    <div className="font-semibold text-sm mt-2 text-zinc-800">{title}</div>
    <div className={`h-2 mt-3 rounded-full ${isCompleted ? 'bg-lime-500' : 'bg-gray-300'}`}></div>
  </div>
);

export default TaskCard;

