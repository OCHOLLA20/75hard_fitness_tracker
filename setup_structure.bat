mkdir alembic
mkdir app
mkdir app\db
mkdir app\schemas
mkdir app\api
mkdir app\api\v1
mkdir app\api\v1\endpoints
mkdir app\core
mkdir app\services
mkdir tests

:: Create files
echo.> app\__init__.py
echo.> app\main.py
echo.> app\config.py
echo.> app\dependencies.py

echo.> app\db\__init__.py
echo.> app\db\database.py
echo.> app\db\models.py

echo.> app\schemas\__init__.py
echo.> app\schemas\user.py
echo.> app\schemas\workout.py
echo.> app\schemas\progress.py
echo.> app\schemas\auth.py

echo.> app\api\__init__.py
echo.> app\api\v1\__init__.py
echo.> app\api\v1\endpoints\__init__.py
echo.> app\api\v1\endpoints\auth.py
echo.> app\api\v1\endpoints\users.py
echo.> app\api\v1\endpoints\workouts.py
echo.> app\api\v1\endpoints\progress.py
echo.> app\api\v1\router.py

echo.> app\core\__init__.py
echo.> app\core\auth.py
echo.> app\core\security.py
echo.> app\core\config.py

echo.> app\services\__init__.py
echo.> app\services\user_service.py
echo.> app\services\workout_service.py
echo.> app\services\stats_service.py

echo.> tests\__init__.py
echo.> tests\conftest.py
echo.> tests\test_auth.py
echo.> tests\test_users.py
echo.> tests\test_workouts.py

echo.> .env
echo.> .gitignore
echo.> requirements.txt
echo.> README.md
echo.> run.py
