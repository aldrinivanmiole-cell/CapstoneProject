# Godot Frontend Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        GODOT MOBILE APP                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                  PRESENTATION LAYER                      │  │
│  │                     (Scenes .tscn)                       │  │
│  │                                                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │  │
│  │  │  Login   │  │ Register │  │MainMenu  │  │ Profile │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │  │
│  │  │ Subjects │  │QuizGame  │  │ Results  │  │Leaderbd │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                    │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │                  CONTROLLER LAYER                        │  │
│  │                   (Scripts .gd)                          │  │
│  │                                                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │LoginCtrl.gd  │  │RegisterCtrl  │  │MainMenuCtrl  │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │SubjectCtrl   │  │QuizCtrl.gd   │  │ResultCtrl    │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐                    │  │
│  │  │LeaderboardCt │  │ProfileCtrl   │                    │  │
│  │  └──────────────┘  └──────────────┘                    │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                    │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │               BUSINESS LOGIC LAYER                       │  │
│  │              (Manager Singletons)                        │  │
│  │                                                          │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │           APIManager.gd (Autoload)              │    │  │
│  │  │  • login_student()                              │    │  │
│  │  │  • register_student()                           │    │  │
│  │  │  • get_student_assignments()                    │    │  │
│  │  │  • submit_assignment()                          │    │  │
│  │  │  • get_leaderboard()                            │    │  │
│  │  │  • Error handling & signals                     │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                           │                              │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │         GameManager.gd (Autoload)               │    │  │
│  │  │  • Student data (id, name, points)              │    │  │
│  │  │  • Scene navigation                             │    │  │
│  │  │  • Assignment state                             │    │  │
│  │  │  • Answer tracking                              │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                           │                              │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │         DataManager.gd (Autoload)               │    │  │
│  │  │  • Session storage                              │    │  │
│  │  │  • Cache management                             │    │  │
│  │  │  • Offline queue                                │    │  │
│  │  │  • Settings persistence                         │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              │ HTTPS/JSON
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      BACKEND SERVER                             │
│                   (FastAPI + Flask)                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API ENDPOINTS                        │   │
│  │                                                         │   │
│  │  POST /api/student/register    → Create account        │   │
│  │  POST /api/student/login       → Authenticate          │   │
│  │  GET  /api/student/{id}/profile → Get profile          │   │
│  │  POST /api/student/subjects    → Get subjects          │   │
│  │  POST /api/student/assignments → Get assignments       │   │
│  │  POST /api/submit/{id}         → Submit answers        │   │
│  │  GET  /api/leaderboard/{code}  → Get rankings          │   │
│  │  POST /api/student/join-class  → Join class            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │                   SQLite Database                       │   │
│  │                     (school.db)                         │   │
│  │                                                         │   │
│  │  • students          → Student accounts                │   │
│  │  • classes           → Class information               │   │
│  │  • assignments       → Assignment data                 │   │
│  │  • questions         → Question bank                   │   │
│  │  • submissions       → Student answers                 │   │
│  │  • enrollments       → Class memberships               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow - Student Takes Quiz

```
┌──────────────┐
│   Student    │
│ Opens App    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ Main.tscn → Check Session                │
│ DataManager.load_session()               │
└──────┬───────────────────────────────────┘
       │
       ├─── No Session ───┐
       │                  │
       │                  ▼
       │          ┌──────────────────┐
       │          │ LoginScreen.tscn │
       │          │ User enters creds│
       │          └────────┬─────────┘
       │                   │
       │                   ▼
       │          ┌────────────────────────┐
       │          │ APIManager.login()     │
       │          │ POST /api/student/login│
       │          └────────┬───────────────┘
       │                   │
       │                   ▼
       │          ┌────────────────────────┐
       │          │ GameManager.login()    │
       │          │ Saves student data     │
       │          └────────┬───────────────┘
       │                   │
       └─── Has Session ───┤
                           │
                           ▼
                  ┌──────────────────┐
                  │  MainMenu.tscn   │
                  │ Shows name/points│
                  └────────┬─────────┘
                           │
                           ▼ (Tap "My Subjects")
                  ┌──────────────────────────┐
                  │ SubjectSelection.tscn    │
                  │ APIManager.get_subjects()│
                  └────────┬─────────────────┘
                           │
                           ▼
                  ┌──────────────────────────┐
                  │ Backend returns subjects │
                  │ ["Math", "Science", ...] │
                  └────────┬─────────────────┘
                           │
                           ▼
                  ┌──────────────────────────┐
                  │ Display subject buttons  │
                  └────────┬─────────────────┘
                           │
                           ▼ (Select "Math")
                  ┌──────────────────────────────┐
                  │ APIManager.get_assignments() │
                  │ POST /api/student/assignments│
                  └────────┬─────────────────────┘
                           │
                           ▼
                  ┌──────────────────────────────┐
                  │ Backend returns assignments  │
                  │ with questions               │
                  └────────┬─────────────────────┘
                           │
                           ▼
                  ┌──────────────────────────────┐
                  │ QuizGame.tscn                │
                  │ QuizController loads questions│
                  └────────┬─────────────────────┘
                           │
                           ▼ (Answer Q1)
                  ┌──────────────────────────────┐
                  │ QuestionHandler renders UI   │
                  │ Student selects answer       │
                  └────────┬─────────────────────┘
                           │
                           ▼ (Submit)
                  ┌──────────────────────────────┐
                  │ GameManager.save_answer()    │
                  │ Stores answer locally        │
                  └────────┬─────────────────────┘
                           │
                           ▼ (Repeat for all questions)
                           │
                           ▼ (Final Submit)
                  ┌──────────────────────────────┐
                  │ APIManager.submit()          │
                  │ POST /api/submit/{id}        │
                  └────────┬─────────────────────┘
                           │
                           ▼
                  ┌──────────────────────────────┐
                  │ Backend grades answers       │
                  │ • Compares with correct      │
                  │ • Calculates score           │
                  │ • Updates student points     │
                  │ • Returns results            │
                  └────────┬─────────────────────┘
                           │
                           ▼
                  ┌──────────────────────────────┐
                  │ ResultScreen.tscn            │
                  │ Shows score, grade, points   │
                  └────────┬─────────────────────┘
                           │
                           ▼
                  ┌──────────────────────────────┐
                  │ GameManager.add_points()     │
                  │ DataManager.save_session()   │
                  └──────────────────────────────┘
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                         SIGNALS FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  APIManager                                                     │
│      │                                                          │
│      ├─ login_completed ────────┐                              │
│      ├─ subjects_loaded ────────┤                              │
│      ├─ assignments_loaded ─────┤                              │
│      ├─ assignment_submitted ───┤                              │
│      └─ api_error ───────────────┼──→ All Controllers listen   │
│                                  │                              │
│  GameManager                     │                              │
│      │                           │                              │
│      └─ student_data_updated ────┘                             │
│                                                                 │
│                                                                 │
│  Controllers                                                    │
│      │                                                          │
│      ├─ Connect to APIManager signals                          │
│      ├─ Update UI based on data                                │
│      └─ Call APIManager methods                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Dependency Tree

```
project.godot
├── Autoloads (Loaded first)
│   ├── APIManager.gd        (No dependencies)
│   ├── GameManager.gd       (Uses: APIManager, DataManager)
│   └── DataManager.gd       (No dependencies)
│
└── Scenes (Loaded on demand)
    ├── Main.tscn
    │   └── Main.gd          (Uses: GameManager, DataManager)
    │
    ├── auth/
    │   ├── LoginScreen.tscn
    │   │   └── LoginController.gd    (Uses: APIManager, GameManager)
    │   └── RegisterScreen.tscn
    │       └── RegisterController.gd (Uses: APIManager, GameManager)
    │
    ├── menu/
    │   ├── MainMenu.tscn
    │   │   └── MainMenuController.gd (Uses: GameManager)
    │   └── SubjectSelection.tscn
    │       └── SubjectSelectionController.gd (Uses: APIManager, GameManager)
    │
    ├── game/
    │   ├── QuizGame.tscn
    │   │   └── QuizController.gd         (Uses: APIManager, GameManager)
    │   │       └── QuestionHandler.gd    (Instanced dynamically)
    │   └── ResultScreen.tscn
    │       └── ResultScreenController.gd (Uses: GameManager, DataManager)
    │
    └── ui/
        ├── Leaderboard.tscn
        │   └── LeaderboardController.gd  (Uses: APIManager, GameManager)
        └── Profile.tscn
            └── ProfileController.gd      (Uses: APIManager, GameManager)
```

## Key Design Patterns

### 1. Singleton Pattern (Autoload)
```
Manager scripts are autoloaded globally:
- Accessible from any script
- Single instance throughout app lifetime
- Persist across scenes
```

### 2. Signal-Based Communication
```
Decoupled architecture:
- Controllers emit/receive signals
- No direct dependencies between controllers
- Easy to modify without breaking others
```

### 3. MVC-Like Pattern
```
Model:      Manager classes (data & logic)
View:       Scene files (.tscn)
Controller: Controller scripts (.gd)
```

### 4. Facade Pattern
```
APIManager acts as facade:
- Hides HTTP complexity
- Provides simple interface
- Handles errors centrally
```

## Summary

This architecture provides:
- ✅ **Separation of Concerns** - Each layer has specific responsibility
- ✅ **Scalability** - Easy to add new scenes/features
- ✅ **Maintainability** - Changes isolated to specific files
- ✅ **Testability** - Managers can be tested independently
- ✅ **Flexibility** - Controllers can be reused
- ✅ **Robustness** - Comprehensive error handling
