@echo off

:MENU
echo =======================================
echo       ContestTrace Menu
echo =======================================
echo 1. Install Dependencies
echo 2. Run Spiders Only
echo 3. Merge Raw Databases
echo 4. Filter Data
echo 5. Export Data to Frontend
echo 6. Start Frontend Server
echo 7. Run Full Process (Spiders->Merge->Filter->Export->Frontend)
echo 0. Exit
echo =======================================
echo Please enter option number:
set /p choice=

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto CRAWL
if "%choice%"=="3" goto MERGE
if "%choice%"=="4" goto FILTER
if "%choice%"=="5" goto EXPORT
if "%choice%"=="6" goto FRONTEND
if "%choice%"=="7" goto FULL_PROCESS
if "%choice%"=="0" goto EXIT

echo Invalid option, please try again!
goto MENU

:INSTALL
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed successfully!
pause
goto MENU

:CRAWL
echo Running spiders (incremental mode)...
python run_teammate_spiders.py
echo Spiders completed successfully!
pause
goto MENU

:MERGE
echo Merging raw databases (today only, preserve existing data)...
python create_raw_db.py
echo Raw databases merged successfully!
pause
goto MENU

:FILTER
echo Filtering data (today only)...
python filter_raw_to_competition.py
echo Data filtered successfully!
pause
goto MENU

:EXPORT
echo Exporting data to frontend...
python run.py --export
echo Data exported successfully!
pause
goto MENU

:FRONTEND
echo Starting frontend server...
echo Please visit http://localhost:8000 in your browser
echo Press Ctrl+C to exit server...
pushd contesttrace\frontend
python -m http.server 8000
popd
goto MENU

:FULL_PROCESS
echo Running full process...
echo.
echo Step 1: Running spiders (incremental mode)...
python run_teammate_spiders.py
echo.
echo Step 2: Merging raw databases (today only, preserve existing data)...
python create_raw_db.py
echo.
echo Step 3: Filtering data (today only)...
python filter_raw_to_competition.py
echo.
echo Step 4: Exporting data to frontend...
python run.py --export
echo.
echo Step 5: Starting frontend server...
echo Please visit http://localhost:8000 in your browser
echo Press Ctrl+C to exit server...
pushd contesttrace\frontend
python -m http.server 8000
popd
goto MENU

:EXIT
echo Exiting program...
exit
