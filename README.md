# 75 Hard Fitness Tracker

A React-based fitness tracker app designed to help you complete the 75 Hard Challenge by tracking daily tasks, visualizing progress, and staying on schedule.

---

## 🚀 Features

- ✅ Track daily challenge tasks
- 📆 View progress across all 75 days
- 📋 Weekly workout planning
- 💪 Reference workout guides
- 📱 Mobile-responsive design
- 💾 LocalStorage for persistent data

---

## 💡 What is the 75 Hard Challenge?

The 75 Hard Challenge is a mental and physical discipline program consisting of the following **daily tasks**, completed for **75 consecutive days**:

1. Two 45-minute workouts (one must be outdoors)
2. Follow a strict diet (no cheat meals or alcohol)
3. Drink 1 gallon (4 liters) of water
4. Take a daily progress photo
5. Read 10 pages of a non-fiction book

---

## 🛠️ Setup Instructions

### Prerequisites

- [Node.js](https://nodejs.org/) and npm installed

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/75hard-fitness-tracker.git
cd 75hard-fitness-tracker

# Install dependencies
npm install

# Start the development server
npm start
```

Visit [http://localhost:3000](http://localhost:3000) to use the app locally.

---

## 📁 File Structure

75hard-fitness-tracker/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── App.js                # Main app component
│   ├── App.css               # Global styles
│   ├── index.js              # Entry point
│   ├── hooks/
│   │   └── useLocalStorage.js  # Custom hook for persistence
├── package.json
└── README.md

---

## 🌐 Deployment

### Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
npm run build
netlify deploy
```

### Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

---

## 🧭 Using the App

### ✅ Today Tab

- Track your daily task completion
- Tasks auto-save as you mark them

### 📅 Schedule Tab

- Plan your weekly workouts
- Use guides for workout ideas

### 📊 Progress Tab

- Monitor your daily/overall progress
- View completion stats and streaks
- Use the 75-day calendar tracker

---

## 🛠️ Customization

- 🎨 Modify color scheme in `App.css` under `:root`
- 💡 Add new workouts or edit routines in the Schedule tab
- 📚 Update or expand workout reference guides

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Contributions

Feel free to fork the repo and submit a pull request with your enhancements!
