from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract, and_, or_, case
import pandas as pd
import calendar

from ..db.models import User, DailyProgress, Workout


def get_challenge_completion_stats(db: Session) -> Dict[str, Any]:
    """
    Get overall statistics about challenge completion across all users.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with challenge completion statistics
    """
    # Total number of users
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    # Users who have started the challenge (have at least one progress record)
    started_users = db.query(func.count(User.id.distinct()))\
        .join(DailyProgress)\
        .scalar() or 0
    
    # Users who have completed the challenge (have 75 completed days)
    completed_users = db.query(func.count(User.id.distinct()))\
        .join(DailyProgress)\
        .group_by(User.id)\
        .having(func.sum(case([(DailyProgress.completed, 1)], else_=0)) >= 75)\
        .scalar() or 0
    
    # Average number of days completed per user
    avg_days = db.query(
            func.avg(
                db.query(func.count(DailyProgress.id))
                .filter(DailyProgress.completed == True)
                .group_by(DailyProgress.user_id)
            )
        ).scalar() or 0
    
    # Average completion rate
    avg_completion_rate = db.query(
            func.avg(
                db.query(func.sum(case([(DailyProgress.completed, 1)], else_=0)) * 100.0 / func.count(DailyProgress.id))
                .group_by(DailyProgress.user_id)
            )
        ).scalar() or 0
    
    return {
        "total_users": total_users,
        "users_started": started_users,
        "users_completed": completed_users,
        "start_rate": round(started_users / total_users * 100, 1) if total_users > 0 else 0,
        "completion_rate": round(completed_users / started_users * 100, 1) if started_users > 0 else 0,
        "avg_days_completed": round(float(avg_days), 1),
        "avg_completion_percentage": round(float(avg_completion_rate), 1)
    }


def get_user_detailed_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a specific user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with detailed user statistics
    """
    # Basic user info
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    # Challenge progress
    progress_records = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(DailyProgress.day_number)\
        .all()
    
    total_days = len(progress_records)
    completed_days = sum(1 for p in progress_records if p.completed)
    
    # Current and longest streaks
    current_streak = 0
    for p in reversed(progress_records):
        if p.completed:
            current_streak += 1
        else:
            break
    
    longest_streak = 0
    current_count = 0
    for p in progress_records:
        if p.completed:
            current_count += 1
            longest_streak = max(longest_streak, current_count)
        else:
            current_count = 0
    
    # Task completion breakdown
    task_completion = {
        "morning_workouts": sum(1 for p in progress_records if p.morning_workout_completed),
        "evening_workouts": sum(1 for p in progress_records if p.evening_workout_completed),
        "diet_adherence": sum(1 for p in progress_records if p.diet_followed),
        "water_intake": sum(1 for p in progress_records if p.water_intake >= 4),
        "progress_photos": sum(1 for p in progress_records if p.progress_photo_taken),
        "reading": sum(1 for p in progress_records if p.reading_completed)
    }
    
    # Calculate task completion percentages
    task_completion_percentage = {
        key: round(value / total_days * 100, 1) if total_days else 0
        for key, value in task_completion.items()
    }
    
    # Failed days analysis - find which requirements are most commonly failed
    failed_days = [p for p in progress_records if not p.completed]
    failure_reasons = {
        "morning_workout": sum(1 for p in failed_days if not p.morning_workout_completed),
        "evening_workout": sum(1 for p in failed_days if not p.evening_workout_completed),
        "diet": sum(1 for p in failed_days if not p.diet_followed),
        "water": sum(1 for p in failed_days if p.water_intake < 4),
        "progress_photo": sum(1 for p in failed_days if not p.progress_photo_taken),
        "reading": sum(1 for p in failed_days if not p.reading_completed)
    }
    
    # Calculate percentages of failure reasons
    num_failed_days = len(failed_days)
    failure_percentage = {
        key: round(value / num_failed_days * 100, 1) if num_failed_days else 0
        for key, value in failure_reasons.items()
    }
    
    # Workout statistics
    workouts = db.query(Workout).filter(Workout.user_id == user_id).all()
    
    workout_categories = {}
    for workout in workouts:
        category = workout.workout_category
        if category in workout_categories:
            workout_categories[category] += 1
        else:
            workout_categories[category] = 1
    
    outdoor_workouts = sum(1 for w in workouts if w.was_outdoor)
    avg_duration = sum(w.duration_minutes for w in workouts) / len(workouts) if workouts else 0
    
    return {
        "username": user.username,
        "challenge_progress": {
            "total_days_tracked": total_days,
            "days_completed": completed_days,
            "days_failed": total_days - completed_days,
            "completion_percentage": round(completed_days / 75 * 100, 1) if completed_days else 0,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "start_date": user.challenge_start_date,
            "expected_end_date": user.challenge_start_date + timedelta(days=74) if user.challenge_start_date else None
        },
        "task_completion": task_completion,
        "task_completion_percentage": task_completion_percentage,
        "failure_analysis": {
            "reasons": failure_reasons,
            "percentages": failure_percentage
        },
        "workout_statistics": {
            "total_workouts": len(workouts),
            "category_distribution": workout_categories,
            "outdoor_percentage": round(outdoor_workouts / len(workouts) * 100, 1) if workouts else 0,
            "avg_duration_minutes": round(avg_duration, 1)
        }
    }


def get_weekly_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get statistics broken down by week for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with weekly statistics
    """
    # Get all progress records for the user
    progress_records = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(DailyProgress.date)\
        .all()
    
    if not progress_records:
        return {"weeks": []}
    
    # Convert to DataFrame for easier analysis
    progress_df = pd.DataFrame([
        {
            "day_number": p.day_number,
            "date": p.date,
            "completed": p.completed,
            "morning_workout": p.morning_workout_completed,
            "evening_workout": p.evening_workout_completed,
            "diet": p.diet_followed,
            "water": p.water_intake >= 4,
            "photo": p.progress_photo_taken,
            "reading": p.reading_completed,
            "week_number": (p.day_number - 1) // 7 + 1
        }
        for p in progress_records
    ])
    
    # Group by week
    weekly_stats = []
    for week_num, week_data in progress_df.groupby("week_number"):
        week_dict = {
            "week_number": int(week_num),
            "start_day": int(week_data["day_number"].min()),
            "end_day": int(week_data["day_number"].max()),
            "start_date": week_data["date"].min().strftime("%Y-%m-%d"),
            "end_date": week_data["date"].max().strftime("%Y-%m-%d"),
            "days_in_week": len(week_data),
            "days_completed": int(week_data["completed"].sum()),
            "completion_percentage": round(week_data["completed"].mean() * 100, 1),
            "task_completion": {
                "morning_workouts": int(week_data["morning_workout"].sum()),
                "evening_workouts": int(week_data["evening_workout"].sum()),
                "diet_adherence": int(week_data["diet"].sum()),
                "water_intake": int(week_data["water"].sum()),
                "progress_photos": int(week_data["photo"].sum()),
                "reading": int(week_data["reading"].sum())
            }
        }
        
        # Calculate task completion percentages
        days_in_week = week_dict["days_in_week"]
        week_dict["task_completion_percentage"] = {
            key: round(value / days_in_week * 100, 1)
            for key, value in week_dict["task_completion"].items()
        }
        
        weekly_stats.append(week_dict)
    
    return {"weeks": weekly_stats}


def get_monthly_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get statistics broken down by month for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with monthly statistics
    """
    # Get all progress records for the user
    progress_records = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(DailyProgress.date)\
        .all()
    
    if not progress_records:
        return {"months": []}
    
    # Convert to DataFrame for easier analysis
    progress_df = pd.DataFrame([
        {
            "day_number": p.day_number,
            "date": p.date,
            "completed": p.completed,
            "morning_workout": p.morning_workout_completed,
            "evening_workout": p.evening_workout_completed,
            "diet": p.diet_followed,
            "water": p.water_intake >= 4,
            "photo": p.progress_photo_taken,
            "reading": p.reading_completed,
            "year_month": p.date.strftime("%Y-%m")
        }
        for p in progress_records
    ])
    
    # Group by month
    monthly_stats = []
    for month_str, month_data in progress_df.groupby("year_month"):
        year, month = month_str.split("-")
        month_name = calendar.month_name[int(month)]
        
        month_dict = {
            "year": int(year),
            "month": int(month),
            "month_name": month_name,
            "start_day": int(month_data["day_number"].min()),
            "end_day": int(month_data["day_number"].max()),
            "start_date": month_data["date"].min().strftime("%Y-%m-%d"),
            "end_date": month_data["date"].max().strftime("%Y-%m-%d"),
            "days_in_month": len(month_data),
            "days_completed": int(month_data["completed"].sum()),
            "completion_percentage": round(month_data["completed"].mean() * 100, 1),
            "task_completion": {
                "morning_workouts": int(month_data["morning_workout"].sum()),
                "evening_workouts": int(month_data["evening_workout"].sum()),
                "diet_adherence": int(month_data["diet"].sum()),
                "water_intake": int(month_data["water"].sum()),
                "progress_photos": int(month_data["photo"].sum()),
                "reading": int(month_data["reading"].sum())
            }
        }
        
        # Calculate task completion percentages
        days_in_month = month_dict["days_in_month"]
        month_dict["task_completion_percentage"] = {
            key: round(value / days_in_month * 100, 1)
            for key, value in month_dict["task_completion"].items()
        }
        
        monthly_stats.append(month_dict)
    
    return {"months": monthly_stats}


def get_weekday_performance(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Analyze performance by day of the week.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with weekday performance analysis
    """
    # Get all progress records for the user
    progress_records = db.query(
            DailyProgress.date, 
            DailyProgress.completed,
            DailyProgress.morning_workout_completed,
            DailyProgress.evening_workout_completed,
            DailyProgress.diet_followed,
            DailyProgress.water_intake,
            DailyProgress.progress_photo_taken,
            DailyProgress.reading_completed
        )\
        .filter(DailyProgress.user_id == user_id)\
        .all()
    
    if not progress_records:
        return {"weekdays": []}
    
    # Convert to DataFrame for easier analysis
    progress_df = pd.DataFrame([
        {
            "date": p.date,
            "weekday": p.date.weekday(),  # 0 = Monday, 6 = Sunday
            "weekday_name": calendar.day_name[p.date.weekday()],
            "completed": p.completed,
            "morning_workout": p.morning_workout_completed,
            "evening_workout": p.evening_workout_completed,
            "diet": p.diet_followed,
            "water": p.water_intake >= 4,
            "photo": p.progress_photo_taken,
            "reading": p.reading_completed
        }
        for p in progress_records
    ])
    
    # Group by weekday
    weekday_stats = []
    for day_num in range(7):  # 0-6 for Monday-Sunday
        day_data = progress_df[progress_df["weekday"] == day_num]
        
        if day_data.empty:
            continue
        
        day_dict = {
            "weekday": day_num,
            "weekday_name": calendar.day_name[day_num],
            "total_occurrences": len(day_data),
            "days_completed": int(day_data["completed"].sum()),
            "completion_percentage": round(day_data["completed"].mean() * 100, 1),
            "task_completion": {
                "morning_workouts": int(day_data["morning_workout"].sum()),
                "evening_workouts": int(day_data["evening_workout"].sum()),
                "diet_adherence": int(day_data["diet"].sum()),
                "water_intake": int(day_data["water"].sum()),
                "progress_photos": int(day_data["photo"].sum()),
                "reading": int(day_data["reading"].sum())
            }
        }
        
        # Calculate task completion percentages
        total_occurrences = day_dict["total_occurrences"]
        day_dict["task_completion_percentage"] = {
            key: round(value / total_occurrences * 100, 1)
            for key, value in day_dict["task_completion"].items()
        }
        
        weekday_stats.append(day_dict)
    
    # Sort by weekday
    weekday_stats.sort(key=lambda x: x["weekday"])
    
    return {"weekdays": weekday_stats}


def get_workout_trends(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Analyze workout trends for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with workout trend analysis
    """
    # Get all workouts for the user
    workouts = db.query(
            Workout.id,
            Workout.workout_type,
            Workout.workout_category,
            Workout.duration_minutes,
            Workout.was_outdoor,
            DailyProgress.date
        )\
        .join(DailyProgress, Workout.daily_progress_id == DailyProgress.id)\
        .filter(Workout.user_id == user_id)\
        .order_by(DailyProgress.date)\
        .all()
    
    if not workouts:
        return {"message": "No workout data found"}
    
    # Convert to DataFrame for easier analysis
    workout_df = pd.DataFrame([
        {
            "id": w.id,
            "date": w.date,
            "type": w.workout_type,
            "category": w.workout_category,
            "duration": w.duration_minutes,
            "outdoor": w.was_outdoor,
            "week": (w.date - workouts[0].date).days // 7 + 1
        }
        for w in workouts
    ])
    
    # Category distribution
    category_counts = workout_df["category"].value_counts().to_dict()
    category_percentages = {
        category: round(count / len(workout_df) * 100, 1)
        for category, count in category_counts.items()
    }
    
    # Outdoor vs Indoor trends
    outdoor_counts = workout_df.groupby("week")["outdoor"].mean() * 100
    outdoor_trend = {
        f"Week {week}": round(percentage, 1)
        for week, percentage in outdoor_counts.items()
    }
    
    # Duration trends
    duration_by_week = workout_df.groupby("week")["duration"].mean()
    duration_trend = {
        f"Week {week}": round(float(duration), 1)
        for week, duration in duration_by_week.items()
    }
    
    # Morning vs Evening workout patterns
    type_distribution = workout_df["type"].value_counts().to_dict()
    type_percentages = {
        workout_type: round(count / len(workout_df) * 100, 1)
        for workout_type, count in type_distribution.items()
    }
    
    # Category trends over time
    category_by_week = workout_df.groupby(["week", "category"]).size().unstack(fill_value=0)
    category_trends = {}
    for week in category_by_week.index:
        week_data = {}
        for category in category_by_week.columns:
            week_data[category] = int(category_by_week.loc[week, category])
        category_trends[f"Week {week}"] = week_data
    
    # Duration by category
    duration_by_category = workout_df.groupby("category")["duration"].mean()
    duration_by_category_dict = {
        category: round(float(duration), 1)
        for category, duration in duration_by_category.items()
    }
    
    return {
        "total_workouts": len(workout_df),
        "category_distribution": {
            "counts": category_counts,
            "percentages": category_percentages
        },
        "workout_type_distribution": {
            "counts": type_distribution,
            "percentages": type_percentages
        },
        "outdoor_workout_trend": outdoor_trend,
        "duration_trend": duration_trend,
        "category_trends": category_trends,
        "avg_duration_by_category": duration_by_category_dict
    }


def get_water_intake_trends(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Analyze water intake trends for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with water intake trend analysis
    """
    # Get all daily progress records for the user
    progress_records = db.query(
            DailyProgress.date,
            DailyProgress.day_number,
            DailyProgress.water_intake
        )\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(DailyProgress.date)\
        .all()
    
    if not progress_records:
        return {"message": "No water intake data found"}
    
    # Convert to DataFrame for easier analysis
    water_df = pd.DataFrame([
        {
            "date": p.date,
            "day_number": p.day_number,
            "water_intake": p.water_intake,
            "week": (p.day_number - 1) // 7 + 1
        }
        for p in progress_records
    ])
    
    # Average water intake by week
    weekly_avg = water_df.groupby("week")["water_intake"].mean()
    weekly_trend = {
        f"Week {week}": round(float(avg), 1)
        for week, avg in weekly_avg.items()
    }
    
    # Days meeting water goal (4L or more)
    met_goal = (water_df["water_intake"] >= 4).sum()
    goal_percentage = round(met_goal / len(water_df) * 100, 1)
    
    # Water intake distribution
    distribution = water_df["water_intake"].value_counts().sort_index().to_dict()
    
    # Moving average (7-day)
    water_df["moving_avg_7day"] = water_df["water_intake"].rolling(window=7, min_periods=1).mean()
    moving_avg = {
        int(row["day_number"]): round(float(row["moving_avg_7day"]), 1)
        for _, row in water_df.iterrows()
    }
    
    return {
        "total_days": len(water_df),
        "average_intake": round(float(water_df["water_intake"].mean()), 1),
        "days_met_goal": int(met_goal),
        "goal_percentage": goal_percentage,
        "weekly_trend": weekly_trend,
        "distribution": distribution,
        "moving_average": moving_avg
    }


def get_comparative_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get statistics comparing the user against averages across all users.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with comparative statistics
    """
    # User's stats
    user_progress = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .all()
    
    if not user_progress:
        return {"message": "No progress data found for this user"}
    
    user_total_days = len(user_progress)
    user_completed_days = sum(1 for p in user_progress if p.completed)
    user_completion_rate = user_completed_days / user_total_days * 100 if user_total_days else 0
    
    # All users with progress
    users_with_progress = db.query(User.id)\
        .join(DailyProgress)\
        .group_by(User.id)\
        .all()
    
    if len(users_with_progress) <= 1:  # Only this user or no users
        return {
            "user_stats": {
                "completion_rate": round(user_completion_rate, 1),
                "total_days": user_total_days,
                "completed_days": user_completed_days
            },
            "message": "Not enough data for comparison"
        }
    
    # Overall averages for all users
    all_completion_rates = []
    all_streaks = []
    all_water_intake = []
    
    for u_id in [u.id for u in users_with_progress]:
        u_progress = db.query(DailyProgress)\
            .filter(DailyProgress.user_id == u_id)\
            .order_by(DailyProgress.day_number)\
            .all()
        
        u_total = len(u_progress)
        u_completed = sum(1 for p in u_progress if p.completed)
        
        if u_total > 0:
            all_completion_rates.append(u_completed / u_total * 100)
        
        # Calculate longest streak
        longest = 0
        current = 0
        for p in u_progress:
            if p.completed:
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        
        all_streaks.append(longest)
        
        # Water intake
        all_water_intake.extend([p.water_intake for p in u_progress])
    
    # User's data
    user_longest_streak = 0
    current_streak = 0
    for p in sorted(user_progress, key=lambda x: x.day_number):
        if p.completed:
            current_streak += 1
            user_longest_streak = max(user_longest_streak, current_streak)
        else:
            current_streak = 0
    
    user_water_intake = [p.water_intake for p in user_progress]
    
    # Calculate averages and user percentile ranks
    avg_completion_rate = sum(all_completion_rates) / len(all_completion_rates)
    avg_longest_streak = sum(all_streaks) / len(all_streaks)
    avg_water_intake = sum(all_water_intake) / len(all_water_intake)
    
    # Percentile calculations
    completion_percentile = sum(1 for r in all_completion_rates if r < user_completion_rate) / len(all_completion_rates) * 100
    streak_percentile = sum(1 for s in all_streaks if s < user_longest_streak) / len(all_streaks) * 100
    water_percentile = sum(1 for w in all_water_intake if w < sum(user_water_intake) / len(user_water_intake)) / len(all_water_intake) * 100
    
    return {
        "user_stats": {
            "completion_rate": round(user_completion_rate, 1),
            "longest_streak": user_longest_streak,
            "avg_water_intake": round(sum(user_water_intake) / len(user_water_intake), 1)
        },
        "average_stats": {
            "completion_rate": round(avg_completion_rate, 1),
            "longest_streak": round(avg_longest_streak, 1),
            "avg_water_intake": round(avg_water_intake, 1)
        },
        "percentile_ranks": {
            "completion_rate": round(completion_percentile, 1),
            "longest_streak": round(streak_percentile, 1),
            "water_intake": round(water_percentile, 1)
        },
        "total_users_compared": len(users_with_progress)
    }


def generate_dashboard_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Generate a comprehensive set of statistics for the user dashboard.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with dashboard statistics
    """
    # Get user and basic progress info
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    progress_records = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(DailyProgress.day_number)\
        .all()
    
    total_days = len(progress_records)
    if total_days == 0:
        return {
            "username": user.username,
            "challenge_started": False,
            "message": "No progress data found. Start the challenge to see statistics."
        }
    
    completed_days = sum(1 for p in progress_records if p.completed)
    current_day = total_days + 1 if total_days < 75 else 75
    
    # Current and longest streaks
    current_streak = 0
    for p in reversed(progress_records):
        if p.completed:
            current_streak += 1
        else:
            break
    
    longest_streak = 0
    current_count = 0
    for p in progress_records:
        if p.completed:
            current_count += 1
            longest_streak = max(longest_streak, current_count)
        else:
            current_count = 0
    
    # Recent progress (last 7 days)
    recent_progress = progress_records[-7:] if len(progress_records) >= 7 else progress_records
    recent_stats = [
        {
            "day_number": p.day_number,
            "date": p.date.strftime("%Y-%m-%d"),
            "completed": p.completed,
            "morning_workout": p.morning_workout_completed,
            "evening_workout": p.evening_workout_completed,
            "diet": p.diet_followed,
            "water_intake": p.water_intake,
            "progress_photo": p.progress_photo_taken,
            "reading": p.reading_completed
        }
        for p in recent_progress
    ]
    
    # Calculate completion by requirement
    requirements_completion = {
        "morning_workouts": sum(1 for p in progress_records if p.morning_workout_completed),
        "evening_workouts": sum(1 for p in progress_records if p.evening_workout_completed),
        "diet_adherence": sum(1 for p in progress_records if p.diet_followed),
        "water_intake": sum(1 for p in progress_records if p.water_intake >= 4),
        "progress_photos": sum(1 for p in progress_records if p.progress_photo_taken),
        "reading": sum(1 for p in progress_records if p.reading_completed)
    }
    
    requirements_percentage = {
        key: round(value / total_days * 100, 1)
        for key, value in requirements_completion.items()
    }
    
    # Challenge dates and timeline
    start_date = user.challenge_start_date
    if start_date:
        expected_end_date = start_date + timedelta(days=74)
        days_since_start = (datetime.now().date() - start_date).days + 1
        days_remaining = 75 - current_day if current_day <= 75 else 0
        
        # Calculate adjusted end date based on failed days
        failed_days = total_days - completed_days
        adjusted_end_date = expected_end_date + timedelta(days=failed_days) if failed_days > 0 else expected_end_date
    else:
        expected_end_date = None
        days_since_start = None
        days_remaining = None
        adjusted_end_date = None
    
    # Monthly progress summary
    if progress_records:
        progress_df = pd.DataFrame([
            {
                "day_number": p.day_number,
                "date": p.date,
                "completed": p.completed,
                "year_month": p.date.strftime("%Y-%m")
            }
            for p in progress_records
        ])
        
        monthly_summary = []
        for month_str, month_data in progress_df.groupby("year_month"):
            year, month = month_str.split("-")
            month_name = calendar.month_name[int(month)]
            
            month_dict = {
                "month": f"{month_name} {year}",
                "days_tracked": len(month_data),
                "days_completed": int(month_data["completed"].sum()),
                "completion_percentage": round(month_data["completed"].mean() * 100, 1)
            }
            
            monthly_summary.append(month_dict)
    else:
        monthly_summary = []
    
    return {
        "username": user.username,
        "challenge_started": True,
        "challenge_progress": {
            "current_day": current_day,
            "total_days_tracked": total_days,
            "days_completed": completed_days,
            "completion_percentage": round(completed_days / 75 * 100, 1),
            "days_remaining": days_remaining
        },
        "streaks": {
            "current_streak": current_streak,
            "longest_streak": longest_streak
        },
        "dates": {
            "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
            "expected_end_date": expected_end_date.strftime("%Y-%m-%d") if expected_end_date else None,
            "adjusted_end_date": adjusted_end_date.strftime("%Y-%m-%d") if adjusted_end_date else None,
            "days_since_start": days_since_start
        },
        "requirements_completion": requirements_completion,
        "requirements_percentage": requirements_percentage,
        "recent_progress": recent_stats,
        "monthly_summary": monthly_summary
    }
