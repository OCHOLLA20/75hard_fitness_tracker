import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './App.css';
import HardTracker from './App';
import reportWebVitals from './reportWebVitals';

// Create a root for concurrent rendering
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the application
root.render(
  <React.StrictMode>
    <HardTracker />
  </React.StrictMode>
);

// Initialize service worker for PWA support
// This registers the service worker for production builds
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('Service Worker registered with scope:', registration.scope);
      })
      .catch(error => {
        console.error('Service Worker registration failed:', error);
      });
  });
}

// If you want to start measuring performance, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint.
// Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

// Add event listener for beforeinstallprompt for PWA install prompt
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Store the event so it can be triggered later
  window.deferredPrompt = e;
  // Update UI to show install button if needed
  // You can use this to implement a custom install button
});

// Local storage initialization - ensures defaults are set
// Only runs on first load if data doesn't exist yet
const initializeLocalStorage = () => {
  // Current day
  if (!localStorage.getItem('currentDayNumber')) {
    localStorage.setItem('currentDayNumber', '1');
  }
  
  // Completed days
  if (!localStorage.getItem('completedDays')) {
    localStorage.setItem('completedDays', '[]');
  }
  
  // Today's tasks
  if (!localStorage.getItem('todayTasks')) {
    const defaultTasks = {
      morningWorkout: false,
      eveningWorkout: false,
      diet: false,
      water1: false,
      water2: false,
      water3: false,
      water4: false,
      progressPhoto: false,
      reading: false
    };
    localStorage.setItem('todayTasks', JSON.stringify(defaultTasks));
  }
  
  // Workouts log
  if (!localStorage.getItem('workouts')) {
    localStorage.setItem('workouts', '{}');
  }
};

// Initialize local storage on app start
initializeLocalStorage();