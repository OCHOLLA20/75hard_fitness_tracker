// Jest DOM testing utilities
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import 'jest-localstorage-mock';

// Configure testing library
configure({ 
  testIdAttribute: 'data-testid',
  // Increase timeout for async tests
  asyncUtilTimeout: 5000 
});

// Mock Lucide React icons component
jest.mock('lucide-react', () => ({
  Calendar: () => <div data-testid="calendar-icon">Calendar Icon</div>,
  CheckSquare: () => <div data-testid="checksquare-icon">CheckSquare Icon</div>,
  Circle: () => <div data-testid="circle-icon">Circle Icon</div>,
  X: () => <div data-testid="x-icon">X Icon</div>,
}));

// Setup mock for localStorage
beforeEach(() => {
  // Clear localStorage before each test
  localStorage.clear();
  
  // Setup initial 75 Hard data structure
  localStorage.setItem('75hard-currentDay', '1');
  localStorage.setItem('75hard-completedDays', '0');
  localStorage.setItem('75hard-dailyTasks', JSON.stringify({
    morningWorkout: false,
    eveningWorkout: false,
    water: 0,
    cleanEating: false,
    progressPhoto: false,
    reading: false
  }));
});

// Custom matchers for 75 Hard specific functionality
expect.extend({
  toBeCompletedTask(received) {
    const pass = received === true;
    return {
      pass,
      message: () => `expected ${received} to be a completed task (true)`,
    };
  },
  
  toHaveWaterLevel(received, expected) {
    const pass = received === expected;
    return {
      pass,
      message: () => `expected water level ${received} to be ${expected}`,
    };
  },
  
  toBeValidDay(received) {
    const pass = received >= 1 && received <= 90;
    return {
      pass,
      message: () => `expected ${received} to be a valid day (1-90)`,
    };
  }
});

// Helper function to simulate completing a day
global.completeDailyTasks = () => {
  localStorage.setItem('75hard-dailyTasks', JSON.stringify({
    morningWorkout: true,
    eveningWorkout: true,
    water: 4,
    cleanEating: true,
    progressPhoto: true,
    reading: true
  }));
};

// Mock date functions
global.mockDate = (isoDate) => {
  const originalDate = global.Date;
  const mockDate = new Date(isoDate);
  
  global.Date = class extends originalDate {
    constructor() {
      super();
      return mockDate;
    }
    
    static now() {
      return mockDate.getTime();
    }
  };
  
  return () => {
    global.Date = originalDate;
  };
};

// Mock window alert
global.alert = jest.fn();

// Clean up after all tests
afterAll(() => {
  localStorage.clear();
  jest.clearAllMocks();
});