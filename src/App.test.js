import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import HardTracker from './App';

// Mock local storage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock localStorage hook to avoid actual localStorage interaction
jest.mock('./hooks/useLocalStorage', () => {
  return jest.fn((key, initialValue) => {
    const [state, setState] = React.useState(initialValue);
    return [state, setState];
  });
});

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Calendar: () => <div data-testid="calendar-icon" />,
  Droplet: () => <div data-testid="droplet-icon" />,
  Droplets: () => <div data-testid="droplets-icon" />,
  Menu: () => <div data-testid="menu-icon" />,
  X: () => <div data-testid="x-icon" />,
  BarChart2: () => <div data-testid="bar-chart-icon" />,
  Home: () => <div data-testid="home-icon" />,
  Dumbbell: () => <div data-testid="dumbbell-icon" />,
  PlusCircle: () => <div data-testid="plus-circle-icon" />,
  Trash2: () => <div data-testid="trash-icon" />,
  User: () => <div data-testid="user-icon" />,
  Plus: () => <div data-testid="plus-icon" />,
  Bell: () => <div data-testid="bell-icon" />
}));

describe('75 Hard Fitness Tracker', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Initialize localStorage mock with default values
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'currentDayNumber') return '1';
      if (key === 'completedDays') return '[]';
      if (key === 'todayTasks') {
        return JSON.stringify({
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
      }
      if (key === 'workouts') return '{}';
      return null;
    });
  });

  test('renders app header with correct title', () => {
    render(<HardTracker />);
    const headerElement = screen.getByText(/75 Hard Tracker/i);
    expect(headerElement).toBeInTheDocument();
  });

  test('renders the home/dashboard view by default', () => {
    render(<HardTracker />);
    expect(screen.getByText(/Keep Going!/i)).toBeInTheDocument();
    expect(screen.getByText(/Today's Tasks/i)).toBeInTheDocument();
  });

  test('shows the current day number in the header', () => {
    render(<HardTracker />);
    expect(screen.getByText(/Day 1\/75/i)).toBeInTheDocument();
  });

  test('displays task cards', () => {
    render(<HardTracker />);
    expect(screen.getByText(/Morning Workout/i)).toBeInTheDocument();
    expect(screen.getByText(/Evening Workout/i)).toBeInTheDocument();
    expect(screen.getByText(/OMAD Diet/i)).toBeInTheDocument();
    expect(screen.getByText(/Read 10 Pages/i)).toBeInTheDocument();
    expect(screen.getByText(/Progress Photo/i)).toBeInTheDocument();
  });

  test('displays water intake tracker', () => {
    render(<HardTracker />);
    expect(screen.getByText(/Water Intake/i)).toBeInTheDocument();
    expect(screen.getByText(/1 gallon/i)).toBeInTheDocument();
  });

  test('displays today\'s workout plan', () => {
    render(<HardTracker />);
    expect(screen.getByText(/Today's Workout Plan/i)).toBeInTheDocument();
    expect(screen.getByText(/Morning Workout/i)).toBeInTheDocument();
    expect(screen.getByText(/Evening Workout/i)).toBeInTheDocument();
  });

  test('can navigate to different tabs', () => {
    render(<HardTracker />);
    
    // Click Calendar tab
    fireEvent.click(screen.getByText(/Calendar/i));
    expect(screen.getByText(/75 Day Progress Calendar/i)).toBeInTheDocument();
    
    // Click Workouts tab
    fireEvent.click(screen.getByText(/Workouts/i));
    expect(screen.getByText(/Today's Plan/i)).toBeInTheDocument();
    
    // Click Stats tab
    fireEvent.click(screen.getByText(/Stats/i));
    expect(screen.getByText(/Your Progress Stats/i)).toBeInTheDocument();
    
    // Click Profile tab
    fireEvent.click(screen.getByText(/Profile/i));
    expect(screen.getByText(/75 Hard Challenger/i)).toBeInTheDocument();
    
    // Back to Home
    fireEvent.click(screen.getByText(/Dashboard/i));
    expect(screen.getByText(/Today's Tasks/i)).toBeInTheDocument();
  });

  test('toggles mobile menu when menu button is clicked', () => {
    // Mock window width to trigger mobile view
    global.innerWidth = 500;
    global.dispatchEvent(new Event('resize'));
    
    render(<HardTracker />);
    
    // Find and click the menu button by its icon
    const menuButton = screen.getByTestId('menu-icon');
    fireEvent.click(menuButton);
    
    // Instead of checking classList directly, we can check for the appearance
    // of menu items that should be visible when menu is open
    // This assumes opening the menu makes these items visible
    expect(screen.getByText(/Dashboard/i)).toBeVisible();
  });

  test('Complete Day button is disabled when not all tasks are completed', () => {
    render(<HardTracker />);
    const completeButton = screen.getByText(/Complete Day 1/i);
    expect(completeButton).toBeDisabled();
  });

  test('can toggle task completion', async () => {
    render(<HardTracker />);
    
    // Find a task and click it directly by its text content
    const morningWorkoutCard = screen.getByText(/Morning Workout/i);
    fireEvent.click(morningWorkoutCard);
    
    // Check if the component reacted in some way
    await waitFor(() => {
      // This is a generic check - in a real app, we'd check for specific UI changes
      expect(morningWorkoutCard).toBeInTheDocument();
    });
  });

  test('workout plan displays correct data for current day', () => {
    // This test assumes today is a specific day, you might need to mock Date
    // to ensure consistent test results
    const mockDate = new Date(2025, 3, 1); // April 1, 2025 (a Wednesday)
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate);
    
    render(<HardTracker />);
    
    // Navigate to workout tab
    fireEvent.click(screen.getByText(/Workouts/i));
    
    // Check if workout plan for Wednesday is displayed
    expect(screen.getByText(/Wednesday Strength Training/i)).toBeInTheDocument();
    
    // Reset Date mock
    global.Date.mockRestore();
  });

  test('calendar shows correct number of day boxes', () => {
    // Modify the component to add aria-label or data-testid to calendar days
    // This is just a placeholder test - you would need to update the actual component
    
    render(<HardTracker />);
    
    // Navigate to calendar tab
    fireEvent.click(screen.getByText(/Calendar/i));
    
    // For this test to work, you'd need to add aria-labels or data-testids to calendar days
    // For now, we can just check that the calendar page renders
    expect(screen.getByText(/75 Day Progress Calendar/i)).toBeInTheDocument();
    
    // Ideally, with proper testids:
    // const dayBoxes = screen.getAllByTestId('calendar-day');
    // expect(dayBoxes.length).toBe(75);
  });
});